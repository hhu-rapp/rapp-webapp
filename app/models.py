import string
import secrets

from app import db
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from os import remove
from pathlib import Path
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from . import login_manager

queried_by: db.Table = db.Table(
    'queried_by',
    db.Column('database_id', db.Integer, db.ForeignKey('ml_databases.id')),
    db.Column('query_id', db.Integer, db.ForeignKey('queries.id'))
)


class MLDatabase(db.Model):     # type: ignore
    def __repr__(self) -> str:
        return f"MLDatabase: ID{self.id}, {self.name}," \
            f"{self.owner.email}, {self.timestamp}"

    __tablename__: str = 'ml_databases'
    __allow_unmapped__ = True

    id: db.Column = db.Column(db.Integer(), primary_key=True)
    name: db.Column = db.Column(db.String(255))
    filename: db.Column = db.Column(db.String(4096))
    user_id: db.Column = db.Column(db.Integer(), db.ForeignKey('users.id'))
    timestamp: db.Column = db.Column(db.DateTime(), default=datetime.utcnow)
    queries: relationship = db.relationship(
        'Query',
        secondary=queried_by,
        backref=db.backref('databases', lazy='dynamic'),
        lazy='dynamic'
    )

    def delete(self):
        filepath: Path = \
            Path(current_app.config['UPLOAD_FOLDER']) / self.filename
        if filepath.exists():
            remove(filepath)

        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class Model(db.Model):      # type: ignore
    def __repr__(self) -> str:
        return f"Model: ID{self.id}"

    id: db.Column = db.Column(db.Integer(), primary_key=True)
    name: db.Column = db.Column(db.String(255))
    model: db.Column = db.Column(db.String(4095))
    timestamp: db.Column = db.Column(db.DateTime(), default=datetime.utcnow)
    query_id: db.Column = db.Column(db.Integer(), db.ForeignKey('queries.id'))

    def save(self):
        db.session.add(self)
        db.session.commit()


class News(db.Model):   # type: ignore
    def __repr__(self) -> str:
        return f'News: {self.id} {self.title}'

    __tablename__: str = 'news'

    id: db.Column = db.Column(db.Integer(), primary_key=True)
    title: db.Column = db.Column(db.String(511))
    text: db.Column = db.Column(db.Text())
    timestamp: db.Column = \
        db.Column(db.DateTime(), default=datetime.utcnow)
    author_id: db.Column = db.Column(db.Integer, db.ForeignKey('users.id'))

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()


class Statistic(db.Model):   # type: ignore
    def __repr__(self) -> str:
        return f'Statistic ID:{self.id}'

    __tablename__: str = 'statistics'

    id: db.Column = db.Column(db.Integer(), primary_key=True)
    title: db.Column = db.Column(db.String(255))
    description: db.Column = db.Column(db.Text())
    img_path: db.Column = db.Column(db.String(4095))


class User(UserMixin, db.Model):  # type: ignore
    """A class representing a user.

    Attributes
    ----------
    password
    id : int
        The ID of the user.
    email : str
        The email address of the user.
    password_hashed : str
        The hashed password of the user.
    is_admin : bool
        A flag showing if a user has admin rights.
    created : DateTime, default: datetime.utcnow
        The DateTime the User was created.
    news : relationship
        A SQLAlchemy-Relationship for newsposts.
    ml_databases: relationship
        A SQLAlchemy-Relationship for databases the User has
        access rights for.

    Methods
    -------
    generate_password() -> str
        Return a random generated password.
    save() -> None
        Save user to database.
    verify_password(password: str) -> bool
        Verify password by matching the provided password against the stored
         hashed password.
    """

    def __repr__(self):
        return f"User ID:{self.id} <{self.email}>, is_admin: {self.is_admin}"

    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password_hashed = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    news = \
        db.relationship('News', backref='author', lazy='dynamic')
    ml_databases = \
        db.relationship('MLDatabase', backref='owner', lazy='dynamic')

    @property
    def password(self) -> None:
        raise AttributeError('Password is not meant to be read.')

    @password.setter
    def password(self, password: str) -> None:
        self.password_hashed = generate_password_hash(password)

    def save(self) -> None:
        """Save user to database."""
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        """Delete user from database."""
        db.session.delete(self)
        db.session.commit()

    def verify_password(self, password) -> bool:
        """Verify password against stored hashed password."""
        return check_password_hash(self.password_hashed, password)

    @staticmethod
    def generate_password() -> str:
        """Return a random generated password."""
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(8))
        return password


class Query(db.Model):      # type: ignore
    def __repr__(self):
        return f"Query ID:{self.id}, {self.name}"

    __tablename__ = 'queries'
    __allow_unmapped__ = True

    id: db.Column = db.Column(db.Integer(), primary_key=True)
    name: db.Column = db.Column(db.String(255))
    query_string: db.Column = db.Column(db.Text())
    timestamp: db.Column = db.Column(db.DateTime(), default=datetime.utcnow)
    model_id: relationship = db.relationship(
        'Model',
        backref='models',
        lazy='dynamic'
    )

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()


@login_manager.user_loader
def load_user(id) -> User:
    return User.query.get(int(id))
