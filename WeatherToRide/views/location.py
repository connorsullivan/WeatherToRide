
from .. import app, csrf, db, forms, models

from ..utils import geocode, validator, weather

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from sqlalchemy import or_

import datetime

# Limit how many locations a user can have at one time
MAX_LOCATIONS = 5

# How old can forecasts be before needing to be refreshed?
MAX_FORECAST_AGE = datetime.timedelta(seconds=900)

def create_or_update_location(user_id, address, name, location_id=None):

    # Validate the user
    user, error = validator.validate_user(user_id)
    if error:
        return None, error

    # Validate the location address
    max_length_address = 255
    if not address or type(address) is not str:
        return 'Location address must be a non-empty string.'
    if len(address) > max_length_address:
        return f'Location address cannot be longer than {max_length_address} characters.'

    # Validate the location name
    max_length_name = models.Location.name.property.columns[0].type.length
    if not name or type(name) is not str:
        return 'Location name must be a non-empty string.'
    if len(name) > max_length_name:
        return f'Location name cannot be longer than {max_length_name} characters.'

    # Validate the current location (if updating instead of creating)
    location = None
    if location_id:
        location, error = validator.validate_location(location_id)
        if error:
            return None, error

    # Create a new location if not updating
    if not location:
        if len(user.locations) < MAX_LOCATIONS:
            location = models.Location(user_id=user.id)
        else:
            return None, 'Location limit has been reached.'

    # Try to get coordinates for the address
    lat, lng, error = geocode.get_coordinates(address)
    if error:
        return None, error

    # Save the new information to this location
    location.lat = lat
    location.lng = lng
    location.name = name

    # Save the location to the database
    db.session.add(location)
    db.session.commit()

    # Try to get the forecast for this location
    weather.update_forecast(location)

    # Return the newly created/updated location
    return location, None

def delete_location(user_id, location_id):

    # Validate the user
    user, error = validator.validate_user(user_id)
    if error:
        return None, error

    # Validate the location
    location, error = validator.validate_location(location_id)
    if error:
        return None, error

    # Make sure the user owns this location
    if location.user != user:
        return None, 'Location does not belong to user.'

    # Delete the forecast for this location
    if location.forecast:
        db.session.delete(location.forecast)
        db.session.commit()

    # Delete any routes using this location
    routes = models.Route.query.filter_by(user_id=user.id)
    routes = routes.filter( or_( models.Route.location_id_1 == location.id, models.Route.location_id_2 == location.id ))
    if routes:
        for route in routes:
            db.session.delete(route)
        db.session.commit()

    # Delete the location
    db.session.delete(location)
    db.session.commit()

    # Return the deleted location
    return location, None

@app.route('/location/create', methods=['GET', 'POST'])
@login_required
def location_create_view():

    # Get a LocationForm from forms.py
    form = forms.LocationForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to add the location to the database
        location, error = create_or_update_location(
            user_id=current_user.id, 
            address=form.address.data, 
            name=form.name.data
        )

        # Check if the location was created
        if location and not error:
            flash('The location was successfully created!', 'success')
            return redirect(url_for('location_view'))
        else:
            flash(error, 'danger')

    # Return the location form
    return render_template('location-form.html', user=current_user, form=form)

@app.route('/api/<key>/location/create', methods=['POST'])
@csrf.exempt
def location_create_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    # Validate the request
    if not request.json:
        abort(400)
    if not 'locationAddress' in request.json:
        abort(400)
    if not 'locationName' in request.json:
        abort(400)

    # Try to add the location to the database
    location, error = create_or_update_location(
        user_id=user.id, 
        address=request.json['locationAddress'], 
        name=request.json['locationName']
    )

    # Check if the location was created
    if location and not error:
        return jsonify({ 'createdLocation': location.serialize() })
    else:
        return jsonify({ 'error': error }), 400

@app.route('/locations')
@login_required
def location_view():

    # Get a SubmitForm from forms.py
    form = forms.SubmitForm()

    # Get this user's locations
    locations = current_user.locations

    # Get the current time
    now = datetime.datetime.now()

    # Update the forecast for locations if needed
    for location in locations:
        if location.forecast:
            forecast_age = now - location.forecast.updated_at
            if forecast_age > MAX_FORECAST_AGE:
                weather.update_forecast(location)
        else:
            weather.update_forecast(location)

    # Get the current date
    today = now.date()

    # Return the location view
    return render_template('locations.html', 
        user=current_user, 
        form=form, 
        locations=locations, 
        day_2=(today + datetime.timedelta(days=2)).strftime('%A'), 
        day_3=(today + datetime.timedelta(days=3)).strftime('%A'), 
        day_4=(today + datetime.timedelta(days=4)).strftime('%A'), 
        day_5=(today + datetime.timedelta(days=5)).strftime('%A'), 
        day_6=(today + datetime.timedelta(days=6)).strftime('%A'), 
        day_7=(today + datetime.timedelta(days=7)).strftime('%A')
    )

@app.route('/api/<key>/locations')
@csrf.exempt
def location_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    length = len(user.locations)
    locations = [x.serialize() for x in user.locations]

    # Get the forecast for each location
    for location in locations:
        location['forecast'] = models.Location.query.get( location['locationId'] ).forecast.serialize()

    return jsonify({ 'userId': user.id, 'numberOfLocations': length, 'locations': locations })

@app.route('/location/update/<int:id>', methods=['GET', 'POST'])
@login_required
def location_update_view(id):

    # Try to find this location in the database
    location = models.Location.query.get(id)
    if not location:
        abort(404)

    # Create a LocationForm with the current values populated
    form = forms.LocationForm(
        address=f'<<<{location.lat},{location.lng}>>>', 
        name=location.name
    )

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to update the location in the database
        location, error = create_or_update_location(
            user_id=current_user.id, 
            address=form.address.data, 
            name=form.name.data, 
            location_id=location.id
        )

        # Check if the location was updated
        if location and not error:
            flash('The location was successfully added!', 'success')
            return redirect(url_for('location_view'))
        else:
            flash(error, 'danger')

    # Return the location form
    return render_template('location-form.html', user=current_user, form=form)

@app.route('/api/<key>/location/update', methods=['POST'])
@csrf.exempt
def location_update_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    # Validate the request
    if not request.json:
        abort(400)
    if not 'locationAddress' in request.json:
        abort(400)
    if not 'locationName' in request.json:
        abort(400)
    if not 'locationId' in request.json:
        abort(400)

    # Try to update the location in the database
    location, error = create_or_update_location(
        user_id=user.id, 
        address=request.json['locationAddress'], 
        name=request.json['locationName'], 
        location_id=request.json['locationId']
    )

    # Check if the location was updated
    if location and not error:
        return jsonify({ 'updatedLocation': location.serialize() })
    else:
        return jsonify({ 'error': error }), 400

@app.route('/location/delete/<int:id>', methods=['POST'])
@login_required
def location_delete_view(id):

    # Get a SubmitForm from forms.py
    form = forms.SubmitForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to delete the location from the database
        location, error = delete_location(
            user_id=current_user.id, 
            location_id=id
        )

        # Check if the location was deleted
        if location and not error:
            flash('The location was successfully deleted!', 'success')
        else:
            flash(error, 'danger')

    # Return to the location view
    return redirect(url_for('location_view'))

@app.route('/api/<key>/location/delete', methods=['POST'])
@csrf.exempt
def location_delete_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    # Validate the request
    if not request.json:
        abort(400)
    if not 'locationId' in request.json:
        abort(400)

    # Try to delete the location from the database
    location, error = delete_location(
        user_id=user.id, 
        location_id=request.json['locationId']
    )

    # Check if the location was deleted
    if location and not error:
        return jsonify({ 'deletedLocation': location.serialize() })
    else:
        return jsonify({ 'error': error }), 400
