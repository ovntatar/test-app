import os
from .context_helpers import register_context_processors
from flask import Flask
from flask import render_template, redirect, url_for, flash, request, current_app
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .extensions import db, migrate, login_mgr
from .models import User
from flask_babel import Babel


# --- SQLite-Fallback, falls _sqlite3 fehlt ---
try:
    import sqlite3  # noqa: F401
except ModuleNotFoundError:
    import sys
    import pysqlite3 as sqlite3  # type: ignore
    sys.modules["sqlite3"] = sqlite3
    sys.modules["_sqlite3"] = sqlite3
# ---------------------------------------------

def get_locale():
    # Check if user is logged in and has language preference
    from flask_login import current_user
    if current_user.is_authenticated and hasattr(current_user, 'language'):
        return current_user.language
    # Otherwise use browser preference or default
    from flask import current_app
    return request.accept_languages.best_match(current_app.config['BABEL_SUPPORTED_LOCALES'])


def _resolve_config(name: str):
    return {
        "DevelopmentConfig": DevelopmentConfig,
        "ProductionConfig": ProductionConfig,
        "TestingConfig": TestingConfig,
    }.get(name, DevelopmentConfig)

def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)
    register_context_processors(app)

   

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    if config_class is None:
        cfg_name = os.getenv("FLASK_CONFIG", "DevelopmentConfig")
        config_class = _resolve_config(cfg_name)

    app.config.from_object(config_class)
    app.config.from_pyfile("config.py", silent=True)

    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_mgr.init_app(app)

    # User loader for Flask-Login
    @login_mgr.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from .blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    from .blueprints.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    from .blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .blueprints.account import bp as account_bp
    app.register_blueprint(account_bp, url_prefix="/account")

    # Admin blueprint - NEW
    from .blueprints.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Health check
    @app.get("/healthz")
    def healthz():
        return {"ok": True}, 200


    from app.security import roles_required

    @app.route("/check-admin")
    @roles_required("admin")
    def check_admin():
        return "You are an admin!"

    @app.route('/debug-locale')
    def debug_locale():
        from flask_login import current_user
        from flask_babel import get_locale
    
        info = {
            'authenticated': current_user.is_authenticated,
            'has_language_attr': hasattr(current_user, 'language') if current_user.is_authenticated else False,
            'user_language': current_user.language if current_user.is_authenticated else None,
            'detected_locale': str(get_locale()),
            'config_locales': current_app.config.get('BABEL_SUPPORTED_LOCALES')
        }
        return info



    # Dev convenience: auto-create tables if none exist
    if app.config.get("ENV") == "development":
        with app.app_context():
            db.create_all()

    return app
