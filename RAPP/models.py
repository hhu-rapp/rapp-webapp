"""Data models."""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from auth import login


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, new_password) -> None:
        self.password = generate_password_hash(new_password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
