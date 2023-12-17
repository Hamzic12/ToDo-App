from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
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
    checkbox = BooleanField("Remember account?")
    submit = SubmitField("Log In")

class Enter_EmailForm(FlaskForm):
    email = StringField(validators=[DataRequired(), Email()])
    send = SubmitField("Send")
class Reset_PasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password"), Length(max=20)])
    confirm = SubmitField("Confirm")

class TodoForm(FlaskForm):
    user_input = StringField(validators=[DataRequired(), Length(max=50)])
    add = SubmitField("Add")
    priority = SelectField(choices=[(0,"priority"),(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5")], coerce=int)
    save = SubmitField("save")