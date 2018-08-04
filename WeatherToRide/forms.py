
from . import models

from flask_wtf import FlaskForm, RecaptchaField

from wtforms import PasswordField, SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from wtforms.widgets import CheckboxInput, ListWidget

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

class EmailForm(FlaskForm):

    email = EmailField( 
        label='Email address', 
        validators=[ DataRequired() ] 
    )

    recaptcha = RecaptchaField()

class PasswordForm(FlaskForm):

    password = PasswordField( 
        label='Password', 
        validators=[ DataRequired(), Length(min=8) ] 
    )

    confirm = PasswordField( 
        label='Confirm password', 
        validators=[ DataRequired(), EqualTo('password') ] 
    )

    recaptcha = RecaptchaField()

class LoginForm(FlaskForm):

    email = EmailField( 
        label='Email address', 
        validators=[ DataRequired() ] 
    )

    password = PasswordField( 
        label='Password', 
        validators=[ DataRequired() ] 
    )

    recaptcha = RecaptchaField()

class UserForm(FlaskForm):

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

    recaptcha = RecaptchaField()

class LocationForm(FlaskForm):

    name = StringField( 
        label='Name of this location', 
        validators=[ DataRequired(), Length(max=32) ], 
        render_kw={"placeholder": "Ray's House"} 
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

    location_id_1 = SelectField('Start destination', coerce=int, validators=[DataRequired()])
    location_id_2 = SelectField('Final destination', coerce=int, validators=[DataRequired()])

    days = MultiCheckboxField('Days for route', coerce=int, choices=[ 
        (0, 'Monday'), 
        (1, 'Tuesday'), 
        (2, 'Wednesday'), 
        (3, 'Thursday'), 
        (4, 'Friday'), 
        (5, 'Saturday'), 
        (6, 'Sunday') 
    ])
