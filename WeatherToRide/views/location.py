
from .. import app, db, forms, models

from ..utils import geocode, weather

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

# Limit how many locations a user can have at one time
MAX_LOCATIONS = 5

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

def create_or_update_location(user_id, name, address, location_id=None):

    # Validate the user
    if not user_id:
        return None, 'User ID cannot be blank.'
    if type(user_id) is not int:
        return None, 'User ID must be an integer.'

    # Find the user in the database
    user = None

    try:
        user = models.User.query.get(int(user_id))
    except:
        return None, 'Error while trying to find user.'

    if not user:
        return None, 'User does not exist.'

    # Validate the location name
    max_length_name = models.Location.name.property.columns[0].type.length

    if not name:
        return None, 'Location name cannot be blank.'
    if type(name) is not str:
        return None, 'Location name must be a string.'
    if len(name) > max_length_name:
        return None, f'Location name cannot be longer than {max_length_name} characters.'

    # Validate the location address
    max_length_address = 255

    if not address:
        return None, 'Location address cannot be blank.'
    if type(address) is not str:
        return None, 'Location address must be a string.'
    if len(address) > max_length_address:
        return None, f'Location address cannot be longer than {max_length_address} characters.'

    # Create a new location
    location = models.Location(user_id=int(user.id))

    # Validate the location (if one already exists)
    if location_id:
        if type(location_id) is not int:
            return None, 'Location ID must be an integer.'

        location = None

        location = models.Location.query.get(int(location_id))

        if not location:
            return None, 'Location does not exist.'

        if location.user_id != user.id:
            return None, 'Location does not belong to user.'

    # Check that the user doesn't have too many locations
    else:
        if len(user.locations) >= MAX_LOCATIONS:
            return None, 'Location limit has been reached.'

    # Get the coordinates from the address
    lat, lng = geocode.get_coordinates(str(address))

    if not lat or not lng:
        return None, 'Address could not be located.'

    # Add the information to the location
    location.name = name
    location.lat = lat
    location.lng = lng

    # Add the location to the database
    db.session.add(location)
    db.session.commit()

    # Get the forecast for this location
    weather.update_forecast(location)

    return location, None

def delete_location(user_id, location_id):

    # Validate the user
    if not user_id:
        return None, 'User ID cannot be blank.'
    if type(user_id) is not int:
        return None, 'User ID must be an integer.'

    # Find the user in the database
    user = None

    try:
        user = models.User.query.get(int(user_id))
    except:
        return None, 'Error while trying to find user.'

    if not user:
        return None, 'User does not exist.'

    # Validate the location
    if not location_id:
        return None, 'Location ID cannot be blank.'
    if type(location_id) is not int:
        return None, 'Location ID must be an integer.'
    
    # Find the location in the database
    location = None

    try:
        location = models.Location.query.get(int(location_id))
    except:
        return None, 'Error while trying to find location.'

    if not location:
        return None, 'Location does not exist.'

    # Make sure the user owns this location
    if location.user.id != user.id:
        return None, 'Location does not belong to user.'

    # Delete any routes using the location
    routes = models.Route.query.filter_by(user_id=user.id)
    routes.filter((models.Route.start == location.id) | (models.Route.final == location.id))
    if routes:
        for route in routes:
            db.session.delete(route)
        db.session.commit()

    # Delete any forecasts for the location
    forecasts = models.Forecast.query.filter_by(location_id=location.id)
    if forecasts:
        for forecast in forecasts:
            db.session.delete(forecast)
        db.session.commit()

    # Delete the location
    db.session.delete(location)
    db.session.commit()

    return location, None

@app.route('/location/create', methods=['GET', 'POST'])
@login_required
def create_location():

    form = forms.LocationForm()

    if form.validate_on_submit():

        # Try to add the location to the database
        location, error = create_or_update_location(
            user_id=current_user.id, 
            name=form.name.data, 
            address=form.address.data
        )

        if location and not error:
            flash('The location was successfully added!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(error, 'danger')

    return render_template('location/location.html', user=current_user, form=form)

@app.route('/location/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_location(id):

    # Try to get the location from the database
    location = models.Location.query.get(int(id))

    if not location:
        abort(404)

    # Create a form with the pre-existing values populated
    form = forms.LocationForm(
        name=location.name, 
        address=f'<<<{location.lat},{location.lng}>>>'
    )

    if form.validate_on_submit():

        # Try to update the location in the database
        location, error = create_or_update_location(
            user_id=current_user.id, 
            name=form.name.data, 
            address=form.address.data, 
            location_id=location.id
        )

        if location and not error:
            flash('The location was successfully added!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(error, 'danger')

    return render_template('location/location.html', user=current_user, form=form)

@app.route('/location/delete/<int:id>', methods=['POST'])
@login_required
def delete_location(id):

    form = forms.SubmitForm()

    if form.validate_on_submit():

        # Try to delete the location
        location, error = delete_location(
            user_id=current_user.id, 
            location_id=id
        )

        if location and not error:
            flash('The location was successfully deleted!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(error, 'danger')

    # Redirect to the dashboard
    return redirect(url_for('dashboard'))
