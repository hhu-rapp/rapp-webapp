from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import main
from .forms import PasswordChangeForm
from ..email import send_email
from ..models import User


@main.route('/reset_password/<int:id>')
@login_required
def reset_password(id):
    user = User.query.get_or_404(id)
    password = User.generate_password()
    user.password = password
    user.save()
    send_email(
        to=user.email,
        subject='Password Reset',
        template='main/email/registration',
        email=user.email,
        password=password
    )
    flash('Password has been changed.')
    return redirect(url_for('main.edit_user', id=id))


@main.route('/profile')
@login_required
def profile():
    page_title = "Profile"
    return render_template('main/profile.html', page_title=page_title)


@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            current_user.save()  # type: ignore
            flash('Password has been updated.')
            return redirect(url_for('main.profile'))
        flash('Wrong password.')
    return render_template('main/change_password.html', form=form)
