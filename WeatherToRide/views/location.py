
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

def create_or_update_location(user_id, name, address, location_id=None):

    # Validate the user
    user, error = validator.validate_user(user_id)
    if error:
        return None, error

    # Validate the location name
    max_length_name = models.Location.name.property.columns[0].type.length

    if not name:
        return 'Location name cannot be blank.'
    if type(name) is not str:
        return 'Location name must be a string.'
    if len(name) > max_length_name:
        return f'Location name cannot be longer than {max_length_name} characters.'

    # Validate the location address
    max_length_address = 255

    if not address:
        return 'Location address cannot be blank.'
    if type(address) is not str:
        return 'Location address must be a string.'
    if len(address) > max_length_address:
        return f'Location address cannot be longer than {max_length_address} characters.'

    # Create a new location
    location = models.Location(user_id=int(user.id))

    # Validate the current location (if updating instead of creating)
    if location_id:
        location, error = validator.validate_location(location_id)
        if error:
            return None, error

    # Check that the user doesn't have too many locations
    else:
        if len(user.locations) >= MAX_LOCATIONS:
            return None, 'Location limit has been reached.'

    # Get the coordinates from the address
    lat, lng, error = geocode.get_coordinates(str(address))

    # If the address could not be found
    if error:
        return None, error

    # Save the new information to this location
    location.name = name
    location.lat = lat
    location.lng = lng

    # Save the location to the database
    db.session.add(location)
    db.session.commit()

    # Get the forecast for this location
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

    # Delete any routes using this location
    routes = models.Route.query.filter_by(user_id=user.id)
    routes = routes.filter(or_(models.Route.location_id_1 == location.id, models.Route.location_id_2 == location.id))
    if routes:
        for route in routes:
            db.session.delete(route)
        db.session.commit()

    # Delete any forecasts for this location
    forecasts = models.Forecast.query.filter_by(location_id=location.id)
    if forecasts:
        for forecast in forecasts:
            db.session.delete(forecast)
        db.session.commit()

    # Delete the location
    db.session.delete(location)
    db.session.commit()

    # Return the deleted route
    return location, None

@app.route('/location/create', methods=['GET', 'POST'])
@login_required
def create_location_view():

    # Get a LocationForm from forms.py
    form = forms.LocationForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to add the location to the database
        location, error = create_or_update_location(
            user_id=current_user.id, 
            name=form.name.data, 
            address=form.address.data
        )

        # Check if the location was added
        if location and not error:
            flash('The location was successfully created!', 'success')
            return redirect(url_for('location_dashboard'))
        else:
            flash(error, 'danger')

    # Return the location template
    return render_template('location-form.html', user=current_user, form=form)

@app.route('/api/<key>/location/create', methods=['POST'])
@csrf.exempt
def create_location_api(key):

    # Validate the API key
    dev = models.Developer.query.filter_by(key=key).first()
    if not dev:
        return jsonify({"error": "Key is invalid."}), 400

    # Find the user for this key
    user = dev.user

    # Check that the request is valid
    if not request.json:
        abort(400)
    if not 'locationName' in request.json:
        abort(400)
    if not 'locationAddress' in request.json:
        abort(400)

    # Try to add the location to the database
    location, error = create_or_update_location(
        user_id=user.id, 
        name=request.json['locationName'], 
        address=request.json['locationAddress']
    )

    # Check if the location was created
    if location and not error:
        return jsonify({"createdLocation": location.serialize()})
    else:
        return jsonify({"error": error}), 400

@app.route('/locations')
@login_required
def location_dashboard():

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

    # Return the location dashboard page
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
def read_locations_api(key):

    # Validate the API key
    dev = models.Developer.query.filter_by(key=key).first()
    if not dev:
        return jsonify({"error": "Key is invalid."}), 400

    # Find the user for this key
    user = dev.user

    length = len(user.locations)
    locations = [x.serialize() for x in user.locations]

    # Get the forecast for each location
    for location in locations:
        location["forecast"] = models.Location.query.get(int(location["locationId"])).forecast.serialize()

    return jsonify({ "userId": user.id, "numberOfLocations": length, "locations": locations })

@app.route('/api/<key>/location/<int:id>')
@csrf.exempt
def read_location_api(key, id):

    # Validate the API key
    dev = models.Developer.query.filter_by(key=key).first()
    if not dev:
        return jsonify({"error": "Key is invalid."}), 400

    # Find the user for this key
    user = dev.user

    # Validate the location
    location, error = validator.validate_location(id)

    if error:
        return jsonify({"error": error}), 400
    
    location = location.serialize()

    # Get the forecast for this location
    location["forecast"] = models.Location.query.get(int(location["locationId"])).forecast.serialize()

    return jsonify({"location": location})

@app.route('/location/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_location_view(id):

    # Try to get the location from the database
    location = models.Location.query.get(int(id))
    if not location:
        abort(404)

    # Create a LocationForm with the current values populated
    form = forms.LocationForm(
        name=location.name, 
        address=f'<<<{location.lat},{location.lng}>>>'
    )

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to update the location in the database
        location, error = create_or_update_location(
            user_id=current_user.id, 
            name=form.name.data, 
            address=form.address.data, 
            location_id=location.id
        )

        # Check if the location was updated
        if location and not error:
            flash('The location was successfully added!', 'success')
            return redirect(url_for('location_dashboard'))
        else:
            flash(error, 'danger')

    # Return the location template
    return render_template('location-form.html', user=current_user, form=form)

@app.route('/api/<key>/location/update', methods=['POST'])
@csrf.exempt
def update_location_api(key):

    # Validate the API key
    dev = models.Developer.query.filter_by(key=key).first()
    if not dev:
        return jsonify({"error": "Key is invalid."}), 400

    # Find the user for this key
    user = dev.user

    # Check that the request is valid
    if not request.json:
        abort(400)
    if not 'locationId' in request.json:
        abort(400)
    if not 'locationName' in request.json:
        abort(400)
    if not 'locationAddress' in request.json:
        abort(400)

    # Try to update the location in the database
    location, error = create_or_update_location(
        user_id=user.id, 
        name=request.json['locationName'], 
        address=request.json['locationAddress'], 
        location_id=request.json['locationId']
    )

    # Check if the location was updated
    if location and not error:
        return jsonify({"updatedLocation": location.serialize()})
    else:
        return jsonify({"error": error}), 400

@app.route('/location/delete/<int:id>', methods=['POST'])
@login_required
def delete_location_view(id):

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

    # Redirect to the dashboard
    return redirect(url_for('location_dashboard'))

@app.route('/api/<key>/location/delete', methods=['POST'])
@csrf.exempt
def delete_location_api(key):

    # Validate the API key
    dev = models.Developer.query.filter_by(key=key).first()
    if not dev:
        return jsonify({"error": "Key is invalid."}), 400

    # Find the user for this key
    user = dev.user

    # Check that the request is valid
    if not request.json:
        abort(400)
    if not 'locationId' in request.json:
        abort(400)

    # Try to delete the location from the database
    location, error = delete_location(
        user.id, 
        request.json['locationId']
    )

    # Check if the location was deleted
    if location and not error:
        return jsonify({"deletedLocation": location.serialize()})
    else:
        return jsonify({"error": error}), 400
