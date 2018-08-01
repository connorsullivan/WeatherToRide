
from .. import app, db, models

import datetime
import requests

'''
    Mapping Dark Sky forecasts to colorful icons

    Icons by: https://www.flaticon.com/
'''
icon_map = { 
    'clear-day': 'clear-day', 
    'clear-night': 'clear-night', 
    'rain': 'rain', 
    'snow': 'snow', 
    'sleet': 'snow', 
    'wind': 'wind', 
    'fog': 'wind', 
    'cloudy': 'cloudy', 
    'partly-cloudy-day': 'cloudy-day', 
    'partly-cloudy-night': 'cloudy-night' 
}

ride_ok = 'Looks like great weather to go for a ride!'
ride_warn = 'It should be ok to ride, but be careful!'
ride_danger = 'It might be a good idea to take the car instead.'

recommendation_map = { 
    'clear-day': ride_ok, 
    'clear-night': ride_ok, 
    'rain': ride_danger, 
    'snow': ride_danger, 
    'sleet': ride_danger, 
    'wind': ride_warn, 
    'fog': ride_warn, 
    'cloudy': ride_ok, 
    'partly-cloudy-day': ride_ok, 
    'partly-cloudy-night': ride_ok 
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

    try:
        key = app.config['DARKSKY_KEY']
    except:
        return None, 'The Dark Sky API is not configured. Weather services are unavailable.'

    # Try to query the Dark Sky API
    try:

        url = f'https://api.darksky.net/forecast/{key}/{lat},{lng}'

        response = requests.get(url).json()

        if not response:
            return None, 'The API returned an empty response.'

    except:
        return None, 'There was a problem while trying to get the weather for this location.'

    # Return the response
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
        return None, 'There was a problem while trying to get the daily forecast for this location.'

    if len(response) < 8:
        return None, f'The daily forecast list received is smaller than expected ({len(daily)} instead of 8).'

    # Get this location's forecast entry from the database
    forecast = models.Forecast.query.filter_by(location_id=location.id).first()

    # If there isn't a pre-existing entry, then create one
    if not forecast:
        forecast = models.Forecast(location_id=location.id)

    # Add the new information to the forecast
    try:

        forecast.day_0_icon = icon_map.get(response[0]['icon'], 'unknown')
        forecast.day_0_summary = response[0]['summary']
        forecast.day_0_recommendation = recommendation_map.get(response[0]['icon'], 'YOLO!')

        forecast.day_1_icon = icon_map.get(response[1]['icon'], 'unknown')
        forecast.day_1_summary = response[1]['summary']
        forecast.day_1_recommendation = recommendation_map.get(response[1]['icon'], 'YOLO!')

        forecast.day_2_icon = icon_map.get(response[2]['icon'], 'unknown')
        forecast.day_2_summary = response[2]['summary']
        forecast.day_2_recommendation = recommendation_map.get(response[2]['icon'], 'YOLO!')

        forecast.day_3_icon = icon_map.get(response[3]['icon'], 'unknown')
        forecast.day_3_summary = response[3]['summary']
        forecast.day_3_recommendation = recommendation_map.get(response[3]['icon'], 'YOLO!')

        forecast.day_4_icon = icon_map.get(response[4]['icon'], 'unknown')
        forecast.day_4_summary = response[4]['summary']
        forecast.day_4_recommendation = recommendation_map.get(response[4]['icon'], 'YOLO!')

        forecast.day_5_icon = icon_map.get(response[5]['icon'], 'unknown')
        forecast.day_5_summary = response[5]['summary']
        forecast.day_5_recommendation = recommendation_map.get(response[5]['icon'], 'YOLO!')

        forecast.day_6_icon = icon_map.get(response[6]['icon'], 'unknown')
        forecast.day_6_summary = response[6]['summary']
        forecast.day_6_recommendation = recommendation_map.get(response[6]['icon'], 'YOLO!')

        forecast.day_7_icon = icon_map.get(response[7]['icon'], 'unknown')
        forecast.day_7_summary = response[7]['summary']
        forecast.day_7_recommendation = recommendation_map.get(response[7]['icon'], 'YOLO!')

    except:
        return None, 'There was a problem extracting forecast data to the database.'

    # Set the update time on the forecast
    forecast.updated_at = datetime.datetime.now()

    # Add the forecast to the database
    db.session.add(forecast)
    db.session.commit()

    # Return the forecast
    return forecast, None
