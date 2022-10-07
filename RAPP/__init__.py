from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)

    # DO NOT USE IN PRODUCTION!
    app.config['SECRET_KEY'] = 'dev'

    from . import ml_visualization
    app.register_blueprint(ml_visualization.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
