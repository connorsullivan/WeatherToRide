
from .. import app, csrf, db, forms, models

from ..utils import geocode, validator, weather

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from sqlalchemy import or_

# Limit how many locations a user can have at one time
MAX_LOCATIONS = 5

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

    return render_template('location.html', user=current_user, form=form)

@app.route('/location/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_location_view(id):

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

    return render_template('location.html', user=current_user, form=form)

@app.route('/location/delete/<int:id>', methods=['POST'])
@login_required
def delete_location_view(id):

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

    # Try to create the location
    location, error = create_or_update_location( 
        user_id=user.id, 
        name=request.json['locationName'], 
        address=request.json['locationAddress'] 
    )

    if error:
        return jsonify({"error": error}), 400
    else:
        return jsonify({"createdLocation": location.serialize()})

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

@app.route('/api/<key>/location')
@csrf.exempt
def read_location_all_api(key):

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

@app.route('/api/<key>/location/update', methods=['PUT'])
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

    # Try to create the location
    location, error = create_or_update_location( 
        user_id=user.id, 
        name=request.json['locationName'], 
        address=request.json['locationAddress'], 
        location_id=request.json['locationId'] 
    )

    if error:
        return jsonify({"error": error}), 400
    else:
        return jsonify({"updatedLocation": location.serialize()})

@app.route('/api/<key>/location/delete', methods=['DELETE'])
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

    # Try to delete the location
    location, error = delete_location(
        user.id, 
        request.json['locationId']
    )

    if error:
        return jsonify({"error": error}), 400
    else:
        return jsonify({"deletedLocation": location.serialize()})
