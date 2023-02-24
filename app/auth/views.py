from flask import (flash, redirect, render_template, request, session, url_for)
from flask_login import current_user, login_required, login_user, logout_user

from . import auth
from .forms import LoginForm
from ..models import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:       # type: ignore
        return redirect(url_for('main.index'))

    form: LoginForm = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            session['email'] = user.email
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Incorrect email or password.')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    session.pop('email')
    logout_user()
    flash('Logged out.')
    return redirect(url_for('auth.login'))
