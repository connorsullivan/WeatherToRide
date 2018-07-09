from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .utilities.validators import Unique
from .models import User

class LoginForm(FlaskForm):

    email = EmailField('Email Address', [
        DataRequired()
    ])

    password = PasswordField('Password', [
        DataRequired()
    ])

class RegistrationForm(FlaskForm):

    email = EmailField('Email Address', [
        DataRequired(), 
        Email(), 
        Unique(User, User.email, message='That e-mail address is already in use.')
    ])

    password = PasswordField('Password', [
        DataRequired(), 
        Length(min=8, message='Your password must be at least 8 characters.')
    ])

    confirm = PasswordField('Confirm Password', [
        DataRequired(), 
        EqualTo('password', message='The passwords do not match.')
    ])

    first_name = StringField('First Name', [
        DataRequired(), 
        Length(max=16)
    ])

    last_name = StringField('Last Name', [
        DataRequired(), 
        Length(max=16)
    ])

    phone = StringField('Phone Number', [
        DataRequired(), 
        Length(min=10, max=10, message='Enter only digits, including area code.'), 
        Unique(User, User.phone, message='That phone number is already in use.')
    ])
