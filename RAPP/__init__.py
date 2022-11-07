from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db: SQLAlchemy = SQLAlchemy()
login_manager: LoginManager = LoginManager()


def create_app() -> Flask:
    """Initialize the core application."""
    app = Flask(__name__)

    # DO NOT USE IN PRODUCTION!
    app.config['MODELS_PATH'] = 'models'
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['UPLOAD_PATH'] = 'uploads'
    app.config['MODEL_FILEFORMAT'] = '.joblib'
    app.config['ML_DB_TYPE'] = 'sqlite'
    app.config['QUERY_FILENAME'] = 'query.sql'

    db.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from . import ml_visualization
    app.register_blueprint(ml_visualization.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
