
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
        lat, lng - The coordinate pair for the requested address

        None, None - If there is an error in processing the request

    """

    # If the address is already resolved, just return the coordinates
    if address.startswith('<<<') and address.endswith('>>>'):
        coords = address.strip('<>')
        try:
            lat, lng = [c.strip() for c in coords.split(',')]
            return lat, lng
        except:
            pass

    # The query string payload for the API request
    payload = {
        'address' : address, 
        'key' : app.config['GOOGLE_KEY']
    }

    # The URL to query the Google Geocoding API
    url = f'https://maps.googleapis.com/maps/api/geocode/json?{urlencode(payload)}'

    try:

        # Extract the JSON response from the API
        response = req.get(url).json()

        # Extract the coordinates from the JSON response
        if response:
            lat = response['results'][0]['geometry']['location']['lat']
            lng = response['results'][0]['geometry']['location']['lng']

            # Return the coordinates
            return lat, lng

        # If there was a problem extracting the coordinates
        else:
            return None, None

    # If there was a problem with the API request
    except:
        return None, None
