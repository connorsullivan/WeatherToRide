
from .. import app

from urllib.parse import urlencode

import requests as req

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

    # Check for the API key
    try:
        payload['key'] = app.config['GOOGLE_KEY']
    except:
        return None, None, 'The Google Geocoding API is not configured. Location services are unavailable.'

    # Try to query the Google Geocoding API
    try:

        url = f'https://maps.googleapis.com/maps/api/geocode/json?{urlencode(payload)}'

        # Extract the JSON response
        response = req.get(url).json()

        # Parse the response for the coordinates
        lat = response['results'][0]['geometry']['location']['lat']
        lng = response['results'][0]['geometry']['location']['lng']

        # Return the coordinates
        return lat, lng, None

    except:
        return None, None, 'There was a problem while trying to find this address.'
