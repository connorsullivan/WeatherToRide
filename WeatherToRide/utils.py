
from . import app

import requests as req

from urllib.parse import urlencode

def coordinates(address):

    payload = {
        'address' : address, 
        'key' : app.config['GOOGLE_KEY']
    }

    api = f'https://maps.googleapis.com/maps/api/geocode/json?{urlencode(payload)}'

    try:
        r = req.get(api).json()

        if r:
            lat = r['results'][0]['geometry']['location']['lat']
            lng = r['results'][0]['geometry']['location']['lng']
            return lat, lng

        else:
            return None, None

    except:
        return None, None

def forecast(latitude, longitude):

    key = app.config['DARKSKY_KEY']

    url = f'https://api.darksky.net/forecast/{key}/{latitude},{longitude}'

    # Query the Dark Sky API
    try:
        response = req.get(url).json()['daily']['data']
    except:
        return None

    # Make sure all of the data was received
    if len(response) < 8:
        return None

    # Assemble the information into a list
    weather = []
    for day in response:
        weather.append( day['icon'] )

    # Return the forecast
    return weather

from wtforms.validators import ValidationError

class Unique(object):

    def __init__(self, model, field, message=u'This is already being used.'):
        self.model = model
        self.field = field
        self.message = message

    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)

from itsdangerous import URLSafeTimedSerializer

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
