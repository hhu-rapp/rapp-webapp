from flask import Blueprint, redirect, url_for
from flask import render_template

from .import db
from .forms import LoginForm, RegisterForm
from .models import User

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    email: str | None = None
    form: LoginForm = LoginForm()

    if form.validate_on_submit():
        email = form.email.data

    return render_template(
        'auth/login.html',
        email=email,
        form=form
    )


@bp.route('/register', methods=['GET', 'POST'])
def register():
    email: str | None = None
    form: RegisterForm = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data

        user: User = User(email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template(
        'auth/register.html',
        email=email,
        form=form
    )
