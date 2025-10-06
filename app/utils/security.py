from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app

def _serializer():
    secret = current_app.config["SECRET_KEY"]
    salt = current_app.config.get("SECURITY_TOKEN_SALT", "change-me")
    return URLSafeTimedSerializer(secret_key=secret, salt=salt)

def generate_token(data: dict) -> str:
    return _serializer().dumps(data)

def verify_token(token: str, max_age: int = 3600):
    try:
        data = _serializer().loads(token, max_age=max_age)
        return True, data
    except SignatureExpired:
        return False, "expired"
    except BadSignature:
        return False, "invalid"
