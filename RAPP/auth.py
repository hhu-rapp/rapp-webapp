from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask_login import current_user
from flask_login import login_user

from .import db
from .forms import LoginForm, RegisterForm
from .models import User

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ml_visualization.home'))

    email: str | None = None
    form: LoginForm = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=form.email.data).first()

        if user is None or not user.check_password(form.password.data):
            print(user)
            return redirect(url_for('auth.login'))

        login_user(user)

        return redirect(url_for('ml_visualization.home'))
    return render_template('auth/login.html', form=form, email=email)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('ml_visualization.home'))

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
