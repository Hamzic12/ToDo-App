from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class SignUpForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=4, max=12)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password"), Length(max=20)])
    submit = SubmitField("Sign Up")

class LogInForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=20)])
    submit = SubmitField("Log In")

class TodoForm(FlaskForm):
    user_input = StringField(validators=[DataRequired(), Length(max=50)])
    add = SubmitField("Add")
