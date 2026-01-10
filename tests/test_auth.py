from flask import request


def test_require_auth_no_token(app, client):
    from app.auth import require_auth

    @app.route('/protected')
    @require_auth
    def protected():
        return "ok", 200

    r = client.get('/protected')
    assert r.status_code == 401


def test_require_auth_valid_token(monkeypatch, app, client):
    from app.auth import require_auth
    import jwt

    # Patch JWKS loader to return a valid key structure
    monkeypatch.setattr('app.auth.get_jwks_client', lambda: {
        "keys": [
            {
                "kid": "test-kid",
                "kty": "RSA",
                "use": "sig",
                "n": "test-modulus",
                "e": "AQAB"
            }
        ]
    })

    # Patch jwt.decode to simulate successful decoding
    monkeypatch.setattr('app.auth.jwt.decode', lambda token, key, algorithms, options: {
        "sub": "user1"
    })

    @app.route('/protected2')
    @require_auth
    def protected2():
        return request.user_id, 200

    # Provide a properly formatted fake JWT token with a valid header and payload
    fake_token = (
        "eyJhbGciOiJSUzI1NiIsImtpZCI6InRlc3Qta2lkIn0."  # Header
        "eyJzdWIiOiJ1c2VyMSJ9."  # Payload
        "c2lnbmF0dXJl"  # Signature (base64-encoded string)
    )

    r = client.get('/protected2', headers={"Authorization": f"Bearer {fake_token}"})
    assert r.status_code == 200
    assert r.get_data(as_text=True) == "user1"
