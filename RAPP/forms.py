"""Form object declaration."""

from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length
from wtforms.validators import ValidationError

from .models import User


class DatabaseUploadForm(FlaskForm):
    """Database upload form."""

    ALLOWED_EXTENSIONS: list[str] = ['sqlite', 'sqlite3', 'db', 'db3', 's3db',
                                     'sl3']

    file_db: FileField = FileField(
        'DatabaseFile',
        validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS)]
    )

    submit = SubmitField('Log In')

    def validate_file_db(self, file):
        """Validate file_db input regarding sqlite format."""

        # TODO
        pass


class LoginForm(FlaskForm):
    """Login form."""
    email: EmailField = EmailField(
        '',
        validators=[Email()],
        render_kw={'placeholder': 'E-Mail'}
    )

    password: PasswordField = PasswordField(
        '',
        validators=[DataRequired()],
        render_kw={'placeholder': 'Password'}
    )

    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    """Register form"""
    email = EmailField(
        'Email',
        validators=[DataRequired(), Email()],
        render_kw={'placeholder': 'E-Mail'}
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=5)],
        render_kw={'placeholder': 'Password'}
    )

    password2 = PasswordField(
        'Repeat Password',
        validators=[
            DataRequired(),
            EqualTo(
                'password',
                'Password and Repeated Password must be equal.'
            )
        ],
        render_kw={'placeholder': 'Repeat Password'}
    )

    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Provided Email already exists.')
