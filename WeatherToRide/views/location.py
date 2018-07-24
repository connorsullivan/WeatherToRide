
from .. import app, db, utils

from ..forms import LocationForm, SubmitForm
from ..models import Location, Route

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from sqlalchemy.exc import IntegrityError

import sys

MAX_LOCATIONS = 3

@app.route('/location/create', methods=['GET', 'POST'])
@login_required
def create_location():

    form = LocationForm()

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # If the user doesn't have too many saved locations
        if len(current_user.locations) < MAX_LOCATIONS:

            # Coordinates are needed to create a location
            lat, lng = None, None

            # Extract the address form field
            address = form.address.data

            # If the user is submitting coordinates, extract them
            if address.startswith('<<<') and address.endswith('>>>'):
                coords = address.strip('<>')
                try:
                    lat, lng = [c.strip() for c in coords.split(',')]
                except:
                    pass
            
            # Otherwise, resolve the coordinates for the given address
            else:
                lat, lng = utils.coordinates(address)

            # Check that the coordinates were resolved correctly
            if lat and lng:

                # Create a new location in the database
                location = Location( 
                    name = form.name.data, 
                    lat = lat, 
                    lng = lng, 
                    user_id = current_user.id 
                )

                db.session.add(location)
                db.session.commit()

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

    # Get the location to be edited from the database
    location = Location.query.get(int(id))

    # Create a form with the pre-existing values already populated
    form = LocationForm(name=location.name, address=f'<<<{location.lat},{location.lng}>>>')

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # Coordinates are needed to create a location
        lat, lng = None, None

        # Extract the address from the form
        address = form.address.data

        # If the user is submitting coordinates, use them directly
        if address.startswith('<<<') and address.endswith('>>>'):
            coords = address.strip('<>')
            try:
                lat, lng = [c.strip() for c in coords.split(',')]
            except:
                pass

        # Otherwise, resolve the coordinates for the given address
        else:
            lat, lng = utils.coordinates(address)

        # Check that the coordinates were resolved correctly
        if lat and lng:

            # Change the information on the location object
            location.name = form.name.data
            location.lat = lat
            location.lng = lng

            # Save the updated location information to the database
            db.session.commit()

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

    form = SubmitForm()

    # If the user is submitting a valid form
    if form.validate_on_submit():

        toDelete = None

        # Make sure the location is one of the user's own
        for location in current_user.locations:
            if location.id == id:
                toDelete = location
                break

        # Delete the given location, if there is one
        if toDelete:

            try:
                db.session.delete(location)
                db.session.commit()
                flash('The location was successfully deleted!', 'success')

            # If the location is used in routes, they must be deleted first
            except IntegrityError:
                flash('Please delete any routes using this location, then try again.', 'danger')

        else:
            flash('You do not have any locations with that ID.', 'danger')

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return redirect(url_for('dashboard'))
