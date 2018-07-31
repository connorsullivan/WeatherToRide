
from .. import app, db, forms, models

from ..utils import validator

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

import datetime

MAX_ROUTES = 5

def create_or_update_route(user_id, name, location_1_id, location_2_id, time, days, route_id=None):

    # Validate the user
    user, error = validator.validate_user(user_id)
    if error:
        return None, error

    # Validate the route name
    if not name:
        return None, 'Route name cannot be blank.'
    if type(name) is not str:
        return None, 'Route name must be a string.'

    max_length_name = models.Route.name.property.columns[0].type.length

    if len(name) > max_length_name:
        return None, f'Route name cannot be longer than {max_length_name} characters.'

    # Validate the first location
    location_1, error = validator.validate_location(location_1_id)
    if error:
        return None, error

    if location_1.user != user:
        return None, 'Starting location does not belong to user.'

    # Validate the second location
    location_2, error = validator.validate_location(location_2_id)
    if error:
        return None, error

    if location_2.user != user:
        return None, 'Ending location does not belong to user.'

    # Make sure the two locations are different
    if location_1 == location_2:
        return None, 'Starting and ending locations must be different.'

    # Validate the time
    if not time:
        return None, 'Time is required.'
    if type(time) is not datetime.time:
        return None, 'Time must be of type datetime.time'

    # Validate the days
    if not days:
        return None, 'Days are required.'
    if type(days) is not list:
        return None, 'Days must be a list of integers.'

    for day in days:
        if type(day) is not int:
            return None, 'All days in list must be integers.'
        if int(day) < 0 or int(day) > 6:
            return None, 'Days in list must be integers between 0 and 6 (inclusive).'

    # Create a new route
    route = models.Route(user_id=int(user.id))

    # Validate the current route (if updating instead of creating)
    if route_id:
        route, error = validator.validate_route(route_id)
        if error:
            return None, error

    # Check that the user doesn't have too many routes
    else:
        if len(user.routes) >= MAX_ROUTES:
            return None, 'Route limit has been reached.'

    # Save the new information to this route
    route.name = name

    route.location_1 = location_1.id
    route.location_2 = location_2.id

    route.time = time

    route.mon = False
    route.tue = False
    route.wed = False
    route.thu = False
    route.fri = False
    route.sat = False
    route.sun = False

    for day in days:
        if day == 0:
            route.mon = True
        if day == 1:
            route.tue = True
        if day == 2:
            route.wed = True
        if day == 3:
            route.thu = True
        if day == 4:
            route.fri = True
        if day == 5:
            route.sat = True
        if day == 6:
            route.sun = True

    # Save the route to the database
    db.session.add(route)
    db.session.commit()

    # Return the newly created/updated route
    return route, None

def delete_route(user_id, route_id):

    # Validate the user
    user, error = validator.validate_user(user_id)
    if error:
        return None, error

    # Validate the route
    route, error = validator.validate_route(route_id)
    if error:
        return None, error

    # Make sure the user owns this route
    if route.user != user:
        return None, 'Route does not belong to user.'

    # Delete the route
    db.session.delete(route)
    db.session.commit()

    # Return the deleted route
    return route, None

@app.route('/route/create', methods=['GET', 'POST'])
@login_required
def create_route_view():

    if len(current_user.locations) < 2:
        flash('You must have at least 2 saved locations before creating a route.', 'danger')
        return redirect(url_for('dashboard'))

    form = forms.RouteForm()

    locations = models.Location.query.filter_by(user_id=current_user.id)

    form.location_1.choices = [(x.id, x.name) for x in locations]
    form.location_2.choices = [(x.id, x.name) for x in locations]

    if form.validate_on_submit():

        route, error = create_or_update_route(
            user_id=current_user.id, 
            name=form.name.data, 
            location_1_id=form.location_1.data, 
            location_2_id=form.location_2.data, 
            time=form.time.data, 
            days=form.days.data
        )

        if route and not error:
            flash('The route was successfully added!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(error, 'danger')

    return render_template('route/route.html', user=current_user, form=form)

@app.route('/route/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_route_view(id):

    route = models.Route.query.get(int(id))

    if not route:
        abort(404)

    days = []

    if route.mon:
        days.append(0)
    if route.tue:
        days.append(1)
    if route.wed:
        days.append(2)
    if route.thu:
        days.append(3)
    if route.fri:
        days.append(4)
    if route.sat:
        days.append(5)
    if route.sun:
        days.append(6)

    form = forms.RouteForm(
        name=route.name, 
        location_1=route.location_1, 
        location_2=route.location_2, 
        time=route.time, 
        days=days
    )

    locations = models.Location.query.filter_by(user_id=current_user.id)

    form.location_1.choices = [(x.id, x.name) for x in locations]
    form.location_2.choices = [(x.id, x.name) for x in locations]

    if form.validate_on_submit():

        route, error = create_or_update_route(
            user_id=current_user.id, 
            name=form.name.data, 
            location_1_id=form.location_1.data, 
            location_2_id=form.location_2.data, 
            time=form.time.data, 
            days=form.days.data, 
            route_id=route.id
        )

        if route and not error:
            flash('The route was successfully updated!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(error, 'danger')

    return render_template('route/route.html', user=current_user, form=form)

@app.route('/route/delete/<int:id>', methods=['POST'])
@login_required
def delete_route_view(id):

    form = forms.SubmitForm()

    if form.validate_on_submit():

        route, error = delete_route(current_user.id, id)

        if route and not error:
            flash('The route was successfully deleted!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(error, 'danger')

    return redirect(url_for('dashboard'))

@app.route('/api/1.0/routes')
@login_required
def read_routes_api():
    return jsonify(len(current_user.routes))
