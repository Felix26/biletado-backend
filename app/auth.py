"""Authentication helpers using Keycloak JWKS.

This module provides a cached JWKS loader and a decorator
('require_auth') that verifies incoming JWTs using the JWKS
published by Keycloak.
"""

import jwt
import json
import requests
from functools import wraps, lru_cache
from typing import Optional, Dict, Any, Callable
from flask import request, jsonify, current_app
from .config import Config

from jwt.algorithms import RSAAlgorithm


@lru_cache(maxsize=1)
def get_jwks_client() -> Optional[Dict[str, Any]]:
    """Fetch the JWKS from Keycloak.

    The result is cached (LRU cache) to avoid repeated network calls.

    Returns:
        A dictionary parsed from the JWKS JSON on success, or 'None' on error.
    """
    try:
        url = Config.KEYCLOAK_CERTS_URL
        return requests.get(url, timeout=3).json()
    except Exception as e:
        current_app.logger.error(f"Could not load JWKS: {e}")
        return None


def require_auth(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that enforces JWT authentication on Flask routes.

    The decorator reads the 'Authorization' header, locates the
    corresponding JWK by 'kid' from the Keycloak JWKS, and verifies the
    token signature. On success it attaches 'user_id' to the Flask
    'request' object (using the token 'sub' or 'preferred_username').
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"errors": [{"code": "not_authorized", "message": "No token"}]}), 401

        try:
            # 1. Wir lesen den Header des Tokens UNVERIFIZIERT, um die Key-ID (kid) zu finden
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = None
            
            # 2. Wir laden die aktuellen Keys von Keycloak
            jwks = get_jwks_client()

            if jwks and "keys" in jwks:
                # 3. Wir suchen den Key, der zur ID im Token passt
                for key in jwks["keys"]:
                    if key["kid"] == unverified_header.get("kid"):
                        # 4. Umwandlung in ein RSA Key Objekt
                        rsa_key = RSAAlgorithm.from_jwk(json.dumps(key))
                        break

            if rsa_key:
                # 5. Erfolgreiche Prüfung mit dem korrekten Key Objekt
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    options={"verify_aud": False}
                )
            else:
                # Kein passender Key gefunden
                current_app.logger.error({
                    "event.action": "auth failed",
                    "event.message": "No matching JWK found"
                })

                return jsonify({"errors": [{"code": "not_authorized", "message": "Invalid token"}]}), 401

            request.user_id = payload.get("sub") or payload.get("preferred_username")

        except jwt.ExpiredSignatureError:
            return jsonify({"errors": [{"code": "not_authorized", "message": "Token expired"}]}), 401
        except Exception as e:
            current_app.logger.error({"event.message": f"Auth Error: {e}"})
            return jsonify({"errors": [{"code": "not_authorized", "message": "Invalid token"}]}), 401

        return f(*args, **kwargs)

    return decorated