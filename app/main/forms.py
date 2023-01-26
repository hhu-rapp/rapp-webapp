from flask_wtf import FlaskForm
from wtforms import (BooleanField, PasswordField, StringField, SubmitField,
                     TextAreaField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)
from flask_wtf.file import FileField, FileRequired

from ..models import User


class NewsForm(FlaskForm):
    title = StringField('Titel', [DataRequired(), Length(1, 511)])
    text = TextAreaField('Text')
    submit = SubmitField('Submit')


class DatabaseForm(FlaskForm):
    name = StringField('Name', [DataRequired(), Length(1, 255)])
    file = FileField('Database', [FileRequired()])
    submit = SubmitField('Submit')

    def validate_file(self, field):
        # TODO
        pass


class QueryForm(FlaskForm):
    name = StringField('Name', [DataRequired(), Length(1, 255)])
    query_string = TextAreaField('Query', [DataRequired()])
    submit = SubmitField()

    def validate_query_string(self, field):
        # TODO
        pass


class RegisterForm(FlaskForm):
    """A User Registration Form for Admins.

    Attributes
    ----------
    email : wtforms.StringField
        A field for submitting the email address of the user.
    """
    email = StringField(
        label='Email',
        validators=[DataRequired(), Email(), Length(1, 255)]
    )
    confirm_send_mail = BooleanField('Confirm', [DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class UserEditAdminForm(FlaskForm):

    def __init__(self, user, *args, **kwargs):
        super(UserEditAdminForm, self).__init__(*args, **kwargs)
        self.user = user

    email = StringField(
        label='Email',
        validators=[DataRequired(), Email(), Length(1, 255)]
    )
    submit = SubmitField('Save')

    def validate_email(self, field):
        if field.data == self.user.email:
            return None
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Old password', [DataRequired()])
    new_password = PasswordField('New password', [DataRequired(), Length(5)])
    new_password_repeat = PasswordField(
        label='Repeat new password',
        validators=[
            DataRequired(),
            EqualTo('new_password', 'Repeated password does not match.')
        ]
    )
    submit = SubmitField('Change password')


class ModelForm(FlaskForm):
    name = StringField('Name', [DataRequired()])
    model_file = FileField('Model', [FileRequired()])
    submit = SubmitField('Submit')
