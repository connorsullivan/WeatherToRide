
from .. import app, db, models

from urllib.parse import urlencode

import datetime
import requests

API_NAME = 'Google Geocode'
MAX_DAILY_CALLS = 1000

def get_coordinates(address):

    """

    Get the latitude and longitude for an address from the Google Geocoding API.

    Args:
        address: An address string to geocode (required)

        The Google Geocoding API is rather forgiving with what it will accept 
            for this parameter. However, best practice is to pass in 
            a complete address, such as the following:

                '1720 2nd Ave S, Birmingham, AL 35294'

    Returns:
        lat, lng, error - The coordinates for the address, plus any error that was caught

        (If there is an error, the values of lat and lng will be None.)

    """

    # If the address is already resolved, just return the coordinates
    if address.startswith('<<<') and address.endswith('>>>'):
        coords = address.strip('<>')

        try:
            lat, lng = [float(c.strip()) for c in coords.split(',')]
            
            if lat < -90 or lat > 90:
                return None, None, 'Latitude is outside of allowable range.'
            if lng < -180 or lng > 180:
                return None, None, 'Longitude is outside of allowable range.'

            return lat, lng, None

        except:
            return None, None, 'There is a problem with the given coordinates.'

    # The payload for the API request
    payload = {'address' : address}

    # Get the current date/time
    now = datetime.datetime.now()

    # Check for the API key
    try:
        payload['key'] = app.config['GOOGLE_KEY']
    except:
        return None, None, 'The Google Geocoding API is not configured. Location services are unavailable.'

    # Get the entry for this API from the database
    status = models.API.query.filter_by(name=API_NAME).first()

    # If there isn't an entry for this API yet
    if not status:
        status = models.API(name=API_NAME)
        status.calls_today = 0
        status.calls_total = 0
        status.last_reset = now
        db.session.add(status)
        db.session.commit()

    # Check if the API call limit needs to be refreshed
    if now.date() > status.last_reset.date():
        status.calls_today = 0
        status.last_reset = now
        db.session.add(status)
        db.session.commit()

    # Check if the API has reached its call limit for today
    if status.calls_today >= MAX_DAILY_CALLS:
        return None, None, 'The location service has reached capacity for today. Geocoding will be unavailable until tomorrow.'
    else:
        status.calls_today += 1
        status.calls_total += 1
        db.session.add(status)
        db.session.commit()

    # Try to query the Google Geocoding API
    try:

        url = f'https://maps.googleapis.com/maps/api/geocode/json?{urlencode(payload)}'

        # Extract the JSON response
        response = requests.get(url).json()

        # Parse the response for the coordinates
        lat = response['results'][0]['geometry']['location']['lat']
        lng = response['results'][0]['geometry']['location']['lng']

        # Return the coordinates
        return lat, lng, None

    except:
        return None, None, 'There was a problem while trying to find this address.'
