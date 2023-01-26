import pytest

from app import create_app, db
from flask.ctx import AppContext


@pytest.fixture()
def app():
    app = create_app('testing')

    app_context: AppContext = app.app_context()
    app_context.push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
