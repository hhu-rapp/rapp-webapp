import os
from flask import Flask

from app import create_app, db
from app.models import Model, User

app: Flask = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return {
        db: db,
        Model: Model,
        User: User
    }
