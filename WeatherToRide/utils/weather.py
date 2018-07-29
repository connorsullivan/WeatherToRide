
from .. import app, db, models

import requests as req

def get_forecast(lat, lng):

    """

    Get a daily weather forecast for a particular location from the Dark Sky API.

    Args:
        lat: Latitude for the location (required)
        lng: Longitude for the location (required)

    Returns:
        A list of dicts [{}, {}, {}]

        Each dictionary represents the forecast for a day of the week, 
            starting with the current day and moving into the future.

        list[0] is for the current day, list[1] is for tomorrow, etc.

        The structure of each dictionary is as follows:

            { 
                'weather': The 'icon' property returned from Dark Sky, 
                'summary': The 'summary' property returned from Dark Sky 
            }

        None if an error was encountered

    """

    # This API key should be kept secret
    key = app.config['DARKSKY_KEY']

    # The URL to query the Dark Sky API
    url = f'https://api.darksky.net/forecast/{key}/{lat},{lng}'

    # Try to get a forecast for the coordinates from Dark Sky
    try:
        response = req.get(url).json()['daily']['data']

    # If there was a problem with the request
    except:
        return None

    # If the data was not fully received
    if len(response) < 8:
        return None

    # Assemble the information into a list of dicts
    forecast = []
    for day in response:
        forecast.append({
            'weather': day['icon'], 
            'summary': day['summary']
        })

    # Return the forecast
    return forecast

def update_forecast(location):

    # Get the forecast for this location
    response = get_forecast(location.lat, location.lng)

    # Get this location's forecast entry from the database
    forecast = models.Forecast.query.filter_by(location_id=location.id).first()

    # If there isn't a pre-existing entry, then create one
    if not forecast:
        forecast = models.Forecast(location_id=location.id)

    # Add the new information to the forecast
    forecast.day_0_weather = response[0]['weather']
    forecast.day_0_summary = response[0]['summary']

    forecast.day_1_weather = response[1]['weather']
    forecast.day_1_summary = response[1]['summary']

    forecast.day_2_weather = response[2]['weather']
    forecast.day_2_summary = response[2]['summary']

    forecast.day_3_weather = response[3]['weather']
    forecast.day_3_summary = response[3]['summary']

    forecast.day_4_weather = response[4]['weather']
    forecast.day_4_summary = response[4]['summary']

    forecast.day_5_weather = response[5]['weather']
    forecast.day_5_summary = response[5]['summary']

    forecast.day_6_weather = response[6]['weather']
    forecast.day_6_summary = response[6]['summary']

    # Add the forecast to the database
    db.session.add(forecast)
    db.session.commit()
