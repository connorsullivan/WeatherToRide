
from flask_wtf import FlaskForm

from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import User
from .utils import Unique

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

    phone = TelField('Phone Number', [
        DataRequired(), 
        Unique(User, User.phone, message='That phone number is already in use.')
    ])

class LocationForm(FlaskForm):

    title = StringField( 
        label = 'Name of this location', 
        validators = [ DataRequired(), Length(max=32) ], 
        render_kw = {"placeholder": "Ray's House"} 
    )

    address = StringField( 
        label = 'Address', 
        validators = [ DataRequired(), Length(max=255) ], 
        render_kw={"placeholder": "1720 2nd Ave S, Birmingham, AL 35294"} 
    )

class DeleteForm(FlaskForm):

    submit = SubmitField()
