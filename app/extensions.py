from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()

login_mgr = LoginManager()
login_mgr.login_view = "auth.login"
login_mgr.login_message_category = "warning"
