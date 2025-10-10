# app/utils/__init__.py should be empty or just have:
from .api_auth import require_api_key, optional_api_key
from .email import send_email, send_confirmation_email, send_password_reset_email
