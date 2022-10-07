"""Form object declaration."""

from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import Length


class LoginForm(FlaskForm):
    """Login form."""
    email: EmailField = EmailField(
        '',
        validators=[Email()],
        render_kw={'placeholder': 'E-Mail'}
    )

    password: PasswordField = PasswordField(
        '',
        validators=[DataRequired(), Length(min=7)],
        render_kw={'placeholder': 'Password'}
    )

    submit = SubmitField('Log In')
