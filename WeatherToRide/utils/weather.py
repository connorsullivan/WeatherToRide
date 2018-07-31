
from .. import app, db, models

import datetime
import requests

'''
    Mapping Dark Sky forecasts to CSS icons

    CSS source: http://erikflowers.github.io/weather-icons/
'''
css_icon_map = { 
    'clear-day': 'wi-day-sunny', 
    'clear-night': 'wi-night-clear', 
    'rain': 'wi-rain', 
    'snow': 'wi-snow', 
    'sleet': 'wi-sleet', 
    'wind': 'wi-windy', 
    'fog': 'wi-fog', 
    'cloudy': 'wi-cloud', 
    'partly-cloudy-day': 'wi-day-cloudy', 
    'partly-cloudy-night': 'wi-night-partly-cloudy' 
}

def get_forecast_from_api(lat, lng):

    """

    Get a daily weather forecast for a particular location from the Dark Sky API.

    Args:
        lat: Latitude for the location (required)
        lng: Longitude for the location (required)

    Returns:
        response, error

        response: The JSON response from the API request (None if error)
        error: First error that was encountered while processing the request (None if success)

    """

    # This API key should be kept secret
    key = app.config['DARKSKY_KEY']

    # The query URL
    url = f'https://api.darksky.net/forecast/{key}/{lat},{lng}'

    # Request a forecast from the Dark Sky API
    response = None
    try:
        response = requests.get(url).json()
    except:
        return None, 'Error while querying API.'

    if not response:
        return None, 'Received empty response from API.'

    return response, None

def update_forecast(location):

    # Get the forecast for this location
    response, error = get_forecast_from_api(location.lat, location.lng)

    # If there was a problem fetching the forecast
    if error:
        return None, error

    # Extract the daily forecasts from the response
    try:
        response = response['daily']['data']
    except:
        return None, 'Error while extracting daily forecasts from response.'

    if len(response) < 8:
        return None, f'Daily forecasts list is smaller than expected ({len(daily)} instead of 8).'

    # Get this location's forecast entry from the database
    forecast = models.Forecast.query.filter_by(location_id=location.id).first()

    # If there isn't a pre-existing entry, then create one
    if not forecast:
        forecast = models.Forecast(location_id=location.id)

    # Add the new information to the forecast
    try:

        forecast.day_0_weather = response[0]['icon']
        forecast.day_0_summary = response[0]['summary']
        forecast.day_0_icon = css_icon_map[response[0]['icon']]

        forecast.day_1_weather = response[1]['icon']
        forecast.day_1_summary = response[1]['summary']
        forecast.day_1_icon = css_icon_map[response[1]['icon']]

        forecast.day_2_weather = response[2]['icon']
        forecast.day_2_summary = response[2]['summary']
        forecast.day_2_icon = css_icon_map[response[2]['icon']]

        forecast.day_3_weather = response[3]['icon']
        forecast.day_3_summary = response[3]['summary']
        forecast.day_3_icon = css_icon_map[response[3]['icon']]

        forecast.day_4_weather = response[4]['icon']
        forecast.day_4_summary = response[4]['summary']
        forecast.day_4_icon = css_icon_map[response[4]['icon']]

        forecast.day_5_weather = response[5]['icon']
        forecast.day_5_summary = response[5]['summary']
        forecast.day_5_icon = css_icon_map[response[5]['icon']]

        forecast.day_6_weather = response[6]['icon']
        forecast.day_6_summary = response[6]['summary']
        forecast.day_6_icon = css_icon_map[response[6]['icon']]

        forecast.day_7_weather = response[7]['icon']
        forecast.day_7_summary = response[7]['summary']
        forecast.day_7_icon = css_icon_map[response[7]['icon']]

    except:
        return None, 'Error while extracting daily forecasts to the model.'

    forecast.updated = datetime.datetime.now()

    # Add the forecast to the database
    db.session.add(forecast)
    db.session.commit()

    return forecast, None
