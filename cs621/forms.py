from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length, EqualTo

from .utilities.validators import Unique
from .models import User

class RegistrationForm(FlaskForm):

    username = StringField('Username', [
        Length(min=4, max=16), 
        Unique(User, User.username, message='That username is not available.')
    ])

    password = PasswordField('Password', [
        Length(min=8), 
        EqualTo('confirm', message='The passwords do not match.')
    ])

    confirm = PasswordField('Confirm Password')

    email = EmailField('Email Address', [
        Unique(User, User.email, message='That e-mail address is already in use.')
    ])

    phone = StringField('Phone Number', [
        Length(min=10, max=10, message='Please enter a US phone number, including area code. Numbers only.'), 
        Unique(User, User.phone, message='That phone number is already in use.')
    ])
