from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from config import config


db: SQLAlchemy = SQLAlchemy()
login_manager: LoginManager = LoginManager()
login_manager.login_view = 'auth.login'     # type: ignore
mail = Mail()


def create_app(config_name: str) -> Flask:
    app: Flask = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .main import main as main_bp
    app.register_blueprint(main_bp)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/auth')

    return app
