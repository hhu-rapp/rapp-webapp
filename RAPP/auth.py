from flask import Blueprint
from flask import render_template

from RAPP.forms import LoginForm

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    email: str = None
    form: LoginForm = LoginForm()

    if form.validate_on_submit():
        email = form.email.data

    return render_template('auth/login.html',
                           email=email,
                           form=form)
