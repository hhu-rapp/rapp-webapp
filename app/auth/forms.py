from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    """A User Login form.

    Attributes
    ----------
    email : wtforms.StringField
        A field for submitting the email address of the user.
    password : wtforms.PasswordField
        A field for submitting the password of the user.
    remember_me : wtforms.BooleanField
        A field for the users intend to stay logged in after leaving the site.
    submit : wtforms.SubmitField
        A submit button.
    """
    email = StringField(
        label='Email',
        validators=[DataRequired(), Email(), Length(1, 255)]
    )
    password = PasswordField('Password', [DataRequired()])
    remember_me = BooleanField('Remember me!')
    submit = SubmitField('Log In')
