
from .. import app, db

from ..forms import DeleteForm, RouteForm
from ..models import Location, Route

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

import sys

MAX_ROUTES = 3

@app.route('/route/create', methods=['GET', 'POST'])
@login_required
def create_route():

    # If the user doesn't have enough locations to create a route
    if len(current_user.locations) < 2:
        flash('You must have at least 2 saved locations before creating a route.', 'danger')
        return redirect(url_for('dashboard'))

    form = RouteForm()

    form.start.choices = [(c.id, c.name) for c in Location.query.filter_by(user_id=current_user.id)]
    form.final.choices = [(c.id, c.name) for c in Location.query.filter_by(user_id=current_user.id)]

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # See how many routes this user already has
        routes = Route.query.filter_by(user_id=current_user.id).all()

        # If the user doesn't have too many routes
        if len(routes) < MAX_ROUTES:

            # Create a new route in the database
            route = Route( 
                name = form.name.data, 
                start = form.start.data, 
                final = form.final.data, 
                user_id = current_user.id 
            )

            db.session.add(route)
            db.session.commit()

            flash(f'{route.name} was successfully added!', 'success')
            return redirect(url_for('dashboard'))

        else:
            flash('Please delete a route before trying to add another.', 'danger')

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return render_template('location/route.html', user=current_user, form=form)

@app.route('/routes/delete/<int:id>', methods=['POST'])
@login_required
def delete_route(id):

    form = DeleteForm()

    # If the user is submitting a valid form
    if form.validate_on_submit():

        toDelete = None

        # Get all of the routes for this user
        routes = Route.query.filter_by(user_id=current_user.id).all()

        # Make sure the route is one of the user's own
        for route in routes:
            if route.id == id:
                toDelete = route
                break

        # Delete the route, if one was found
        if toDelete:
            db.session.delete(route)
            db.session.commit()
            flash('The route was deleted.', 'success')

        else:
            flash('You do not have any routes with that ID.', 'danger')

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return redirect(url_for('dashboard'))
