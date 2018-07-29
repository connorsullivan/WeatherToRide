
from .. import app, db, forms, models

from ..utils import geocode, weather

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from sqlalchemy.exc import IntegrityError

import sys

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

@app.route('/location/create', methods=['GET', 'POST'])
@login_required
def create_location():

    form = forms.LocationForm()

    if form.validate_on_submit():

        # If the user doesn't have too many saved locations
        if len(current_user.locations) < MAX_LOCATIONS:

            # Get the coordinates from the address
            lat, lng = geocode.get_coordinates(form.address.data)

            # Check that the coordinates were resolved correctly
            if lat and lng:

                # Create a new location in the database
                location = models.Location( 
                    name = form.name.data, 
                    lat = lat, 
                    lng = lng, 
                    user_id = current_user.id 
                )

                # Add the location to the database
                db.session.add(location)
                db.session.commit()

                # Get the weather for this new location
                weather.update_forecast(location)

                flash('The location was successfully added!', 'success')
                return redirect(url_for('dashboard'))

            else:
                flash('Please make sure the address is valid.', 'danger')

        else:
            flash('Please delete a location before trying to add another.', 'danger')

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return render_template('location/location.html', user=current_user, form=form)

@app.route('/location/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_location(id):

    # Get the location from the database
    location = models.Location.query.get(int(id))

    # Create a form with the pre-existing values already populated
    form = forms.LocationForm(name=location.name, address=f'<<<{location.lat},{location.lng}>>>')

    if form.validate_on_submit():

        # Get the coordinates from the address
        lat, lng = geocode.get_coordinates(form.address.data)

        # Check that the coordinates were resolved correctly
        if lat and lng:

            # Change the information on the location object
            location.name = form.name.data
            location.lat = lat
            location.lng = lng

            # Save the updated location information to the database
            db.session.commit()

            # Get the weather for this location
            weather.update_forecast(location)

            flash('The location was successfully updated!', 'success')

            return redirect(url_for('dashboard'))

        else:
            flash('Please make sure the address is valid.', 'danger')

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return render_template('location/location.html', user=current_user, form=form)

@app.route('/location/delete/<int:id>', methods=['POST'])
@login_required
def delete_location(id):

    # Get an instance of the SubmitForm from forms.py
    form = forms.SubmitForm()

    # If a valid SubmitForm was submitted
    if form.validate_on_submit():

        # This will hold the location to be deleted
        toDelete = None

        # Find the location to be deleted from the user's locations
        for location in current_user.locations:
            if location.id == id:
                toDelete = location
                break

        # If a matching location was found
        if toDelete:

            # Delete any routes using the location
            routes = models.Route.query.filter_by(user_id=current_user.id)
            routes.filter((models.Route.start == id) | (models.Route.final == id))
            if routes:
                for route in routes:
                    db.session.delete(route)
                db.session.commit()

            # Delete any forecasts for the location
            forecasts = models.Forecast.query.filter_by(location_id=id)
            if forecasts:
                for forecast in forecasts:
                    db.session.delete(forecast)
                db.session.commit()

            # Delete the location
            db.session.delete(location)

            # Commit the changes to the database
            db.session.commit()

            # Flash a confirmation message to the user
            flash('The location was successfully deleted!', 'success')

        # If a matching location was not found
        else:
            flash('You do not have any locations with that ID.', 'danger')

    # If the submitted form has errors
    if form.errors:

        # Log the errors to the console
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    # Redirect to the dashboard
    return redirect(url_for('dashboard'))
