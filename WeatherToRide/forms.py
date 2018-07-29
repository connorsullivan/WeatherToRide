
from . import models

from flask_wtf import FlaskForm

from wtforms import PasswordField, SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.fields.html5 import EmailField, TelField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget

import datetime

class MultiCheckboxField(SelectMultipleField):

    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class Unique(object):

    def __init__(self, model, field, message='This element already exists.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)

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
        Unique(models.User, models.User.email, message='That e-mail address is already in use.')
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
        Unique(models.User, models.User.phone, message='That phone number is already in use.')
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

    time = TimeField('Departure time')

    days = MultiCheckboxField('Days of week', coerce=int, choices=[
        (0, 'Monday'), 
        (1, 'Tuesday'), 
        (2, 'Wednesday'), 
        (3, 'Thursday'), 
        (4, 'Friday'), 
        (5, 'Saturday'), 
        (6, 'Sunday')
    ])

class SubmitForm(FlaskForm):

    submit = SubmitField()
