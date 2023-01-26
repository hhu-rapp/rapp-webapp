from flask import abort
from flask_login import current_user
from functools import wraps
from typing import Callable


def admin_required(func: Callable) -> Callable:
    """ A decorator for admin only access routes."""
    @wraps(func)
    def wrapper_admin_required(*args: list, **kwargs: dict):
        if not current_user.is_admin:   # type:ignore
            abort(403)
        return func(*args, **kwargs)
    return wrapper_admin_required
