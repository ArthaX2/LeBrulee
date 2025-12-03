from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import EqualTo, Length, DataRequired


class ResetUserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters."),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("new_password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Reset Password")