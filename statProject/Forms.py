from flask_wtf import FlaskForm
##from flask_wtf.file import FileField, FileAllowed
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    userName = StringField('User name',validators=[DataRequired(), Length(min=2, max=15, message= 'user name should be at least 2 characters long and at most 15. Please try another.')])
    email = StringField('Email',validators=[DataRequired(), Email(message = 'Enter the email address in the format "someone@example.com".')])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email(message = 'Invaild email address')])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AccountForm(FlaskForm):
    username = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=15, message= 'user name should be at least 2 characters long and at most 15. Please try another.')])
    picture = FileField('Update Profile Picture', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
    bio = StringField('Biography')
    submit = SubmitField('Update')
