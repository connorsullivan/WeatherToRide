
from flask_wtf import FlaskForm

from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .models import User, Location
from .utils import Unique

class LoginForm(FlaskForm):

    email = EmailField('Email address', [
        DataRequired()
    ])

    password = PasswordField('Password', [
        DataRequired()
    ])

class RegistrationForm(FlaskForm):

    email = EmailField('Email address', [
        DataRequired(), 
        Email(), 
        Length(max=32), 
        Unique(User, User.email, message='That e-mail address is already in use.')
    ])

    password = PasswordField('Password', [
        DataRequired(), 
        Length(min=8, message='Your password must be at least 8 characters.')
    ])

    confirm = PasswordField('Confirm password', [
        DataRequired(), 
        EqualTo('password', message='The passwords do not match.')
    ])

    name = StringField('First name', [
        DataRequired(), 
        Length(max=32)
    ])

    phone = TelField('Phone number', [
        DataRequired(), 
        Length(max=10), 
        Unique(User, User.phone, message='That phone number is already in use.')
    ])

class LocationForm(FlaskForm):

    name = StringField( 
        label = 'Name of this location', 
        validators = [ DataRequired(), Length(max=32) ], 
        render_kw = {"placeholder": "Ray's House"} 
    )

    address = StringField( 
        label = 'Address', 
        validators = [ DataRequired(), Length(max=255) ], 
        render_kw={"placeholder": "1720 2nd Ave S, Birmingham, AL 35294"} 
    )

class RouteForm(FlaskForm):

    name = StringField( 
        label = 'Name of this route', 
        validators = [ DataRequired(), Length(max=32) ], 
        render_kw = {'placeholder': 'Work commute'} 
    )

    start = SelectField('Start destination', coerce=int, validators=[DataRequired()])
    final = SelectField('Final destination', coerce=int, validators=[DataRequired()])

class SubmitForm(FlaskForm):

    submit = SubmitField()
