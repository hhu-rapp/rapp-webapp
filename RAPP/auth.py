from flask import Blueprint
from flask import render_template

bp = Blueprint('auth', __name__)


@bp.route('/login')
def login():
    return render_template('auth/login.html')
