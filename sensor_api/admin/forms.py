from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(max=140)
        ]
    )
    username = StringField(
        "E-Mail Address",
        validators=[DataRequired()]
    )


class RegisterForm(Form):
    email = StringField(
        "E-Mail Address",
        validators=[DataRequired()]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(max=140)
        ]
    )