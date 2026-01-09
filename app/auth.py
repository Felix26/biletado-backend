import jwt
import requests
from functools import wraps, lru_cache
from flask import request, jsonify, current_app

from .config import Config

# lru_cache speichert das Ergebnis, damit wir Keycloak nicht bei jedem Request fragen
@lru_cache(maxsize=1)
def get_keycloak_pem():
    try:
        url = Config.KEYCLOAK_URL
        data = requests.get(url, timeout=3).json()
        return f"-----BEGIN PUBLIC KEY-----\n{data['public_key']}\n-----END PUBLIC KEY-----"
    except Exception as e:
        current_app.logger.error(f"Keycloak Error: {e}")
        return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"errors": [{"code": "not_authorized", "message": "No token"}]}), 401

        # 2. Key holen & Token prüfen
        public_key = get_keycloak_pem()
        
        try:
            if public_key:
                # Echte Prüfung
                jwt.decode(token, public_key, algorithms=["RS256"], options={"verify_aud": False})
            else:
                # Fallback für Dev/Offline (ohne Prüfung)
                jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return jsonify({"errors": [{"code": "not_authorized", "message": "Invalid token"}]}), 401

        return f(*args, **kwargs)
    return decorated