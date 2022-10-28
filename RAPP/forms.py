"""Form object declaration."""

from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import InputRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError

from .models import User


class DatabaseUploadForm(FlaskForm):
    """Database upload form."""

    ALLOWED_EXTENSIONS: list[str] = ['sqlite', 'sqlite3', 'db', 'db3', 's3db',
                                     'sl3']

    ml_db_file: FileField = FileField(
        'New database',
        validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS)]
    )

    def validate_ml_db_file(self, file):
        """Validate ml_db_file input regarding sqlite format."""

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


class QuerySelectForm(FlaskForm):
    """Query Selection form"""
    query = SelectField(
        'Select Query',
        validators=[InputRequired()]
    )
    submit = SubmitField('Select')

    def edit_queries(self, choices: list[tuple[str, str]]) -> None:
        """Set query choices.

        Parameters
        ----------
        choices: list[tuple[str, str]]
            The queries the Query-SelectField will offer to the user
            as a list of (value, label) pairs.
        """
        self.query.choices = choices


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
