
from .. import app, db, utils

from ..forms import DeleteForm, LocationForm
from ..models import Location

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

import sys

@app.route('/locations/new', methods=['GET', 'POST'])
@login_required
def create_location():

    form = LocationForm()

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # If the user has less than the maximum number of saved locations
        if len(current_user.locations) < 3:

            # Get the coordinates for the address
            lat, lng = utils.coordinates(form.address.data)

            # Check that the coordinates were resolved correctly
            if lat and lng:

                # Create a new location in the database
                location = Location( 
                    user_id = current_user.id, 
                    title = form.title.data, 
                    lat = lat, 
                    lng = lng 
                )

                db.session.add(location)
                db.session.commit()

                flash(f'{form.title.data} was successfully added!', 'success')
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

@app.route('/locations/delete/<int:id>', methods=['POST'])
@login_required
def delete_location(id):

    form = DeleteForm()

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
            db.session.delete(location)
            db.session.commit()
            flash('Location removed.', 'success')

        else:
            flash('You do not have any locations with the given ID.', 'danger')

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return redirect(url_for('dashboard'))
