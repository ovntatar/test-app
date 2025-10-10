import os


class Config:
    # Existing config...
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'de']
    BABEL_TRANSLATION_DIRECTORIES = 'translations'

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.sqlite3")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None
    PREFERRED_URL_SCHEME = "https"
    SECURITY_TOKEN_SALT = os.getenv("SECURITY_TOKEN_SALT", "change-me")

    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

    # Babel i18n settings
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'de']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'translations')
    
    # Stripe Configuration
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@yourapp.com")
    
    # App Info
    APP_NAME = os.getenv("APP_NAME", "YourApp")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@yourapp.com")

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    # In development, don't send real emails
    MAIL_SUPPRESS_SEND = True

class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"
    # In production, send real emails
    MAIL_SUPPRESS_SEND = False

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    MAIL_SUPPRESS_SEND = True
