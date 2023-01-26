from flask import Flask
from os import environ
from pathlib import Path
from typing import Type

base_dir: Path = Path.cwd()


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    Parameters
    ----------
    val : str
        The string to be converted into a boolean value.

    Attributes
    ----------
    TRUTHY_VALS : tuple[str, str, str, str, str, str]
        Truthy values will be converted to True.
    FALSY_VALS : tuple[str, str, str, str, str, str]
        Falsy values will be converted to False.

    Returns
    -------
    The boolean value of the string val.

    Raises
    ------
    ValueError
        If val is neither a known truthy nor falsy value.
    """
    TRUTHY_VALS: tuple[str, str, str, str, str, str] = \
        ('y', 'yes', 't', 'true', 'on', '1')
    FALSY_VALS: tuple[str, str, str, str, str, str] = \
        ('n', 'no', 'f', 'false', 'off', '0')

    val = val.lower()
    if val in TRUTHY_VALS:
        return True
    elif val in FALSY_VALS:
        return False
    else:
        raise ValueError(f"invalid truth value {val}")


class Config:
    UPLOAD_FOLDER: str = 'uploads'
    SECRET_KEY: str = environ.get('SECRET_KEY') or '8wGoFN3upjpWAmCnwq2AnQ'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    MAIL_SERVER: str | None = environ.get('MAIL_SERVER')
    MAIL_PORT: int | None = int(environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS: bool | None = strtobool(environ.get('MAIL_USE_TLS', 'false'))
    MAIL_USERNAME: str | None = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD: str | None = environ.get('MAIL_PASSWORD')
    RAPP_MAIL_SUBJECT_PREFIX: str = '[RAPP] '
    RAPP_MAIL_SENDER: str = f"RAPP Admin <{environ.get('MAIL_SENDERNAME')}>"

    @staticmethod
    def init_app(app: Flask) -> None:
        pass


class DevConfig(Config):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = environ.get('DATABASE_URL_DEV') or \
        'sqlite:///' + str(base_dir / 'data' / 'database-dev.sqlite')
    MAIL_SUPPRESS_SEND: bool = False


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI: str = environ.get('DATABASE_URL_TEST') or \
        'sqlite:///'
    TESTING: bool = True
    WTF_CSRF_ENABLED = False


class ProdConfig(Config):
    SECRET_KEY: str | None = environ.get('SECRET_KEY')


config: dict[str, Type[Config]] = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig
}
