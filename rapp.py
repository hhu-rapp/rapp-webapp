import os
import sys

from flask import Flask

from app import create_app, db
from app.models import Model, User

# Change working directory to the directory of the executable
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)
    app: Flask = create_app('development')
    app.run(debug=True)
else:
    app: Flask = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return {
        db: db,
        Model: Model,
        User: User
    }
