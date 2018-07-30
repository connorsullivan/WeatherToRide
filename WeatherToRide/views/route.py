
from .. import app, db, forms, models

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

import datetime

MAX_ROUTES = 5

def create_or_update_route(user_id, name, location_1_id, location_2_id, time, days, route_id=None):

    if not user_id:
        return None, 'User ID cannot be blank.'
    if type(user_id) is not int:
        return None, 'User ID must be an integer.'

    user = None

    try:
        user = models.User.query.get(int(user_id))
    except:
        return None, 'Error while trying to find user.'

    if not user:
        return None, 'User does not exist.'

    max_length_name = models.Route.name.property.columns[0].type.length

    if not name:
        return None, 'Route name cannot be blank.'
    if type(name) is not str:
        return None, 'Route name must be a string.'
    if len(name) > max_length_name:
        return None, f'Route name cannot be longer than {max_length_name} characters.'

    if not location_1_id:
        return None, 'First location ID is required.'
    if type(location_1_id) is not int:
        return None, 'First location ID must be an integer.'

    location_1 = None

    try:
        location_1 = models.Location.query.get(int(location_1_id))
    except:
        return None, 'Error while trying to find first location.'

    if not location_1:
        return None, 'First location does not exist.'

    if location_1.user_id != user.id:
        return None, 'First location does not belong to user.'

    if not location_2_id:
        return None, 'Second location ID is required.'
    if type(location_2_id) is not int:
        return None, 'Second location ID must be an integer.'

    location_2 = None

    try:
        location_2 = models.Location.query.get(int(location_2_id))
    except:
        return None, 'Error while trying to find second location.'

    if not location_2:
        return None, 'Second location does not exist.'

    if location_2.user_id != user.id:
        return None, 'Second location does not belong to user.'

    if location_1 == location_2:
        return None, 'First and second locations must be different.'

    if not time:
        return None, 'Time is required.'
    if type(time) is not datetime.time:
        return None, 'Time must be of type datetime.time'

    if not days:
        return None, 'Days are required.'
    if type(days) is not list:
        return None, 'Days must be a list of integers.'

    for day in days:
        if type(day) is not int:
            return None, 'All days in list must be integers.'
        if int(day) < 0 or int(day) > 6:
            return None, 'Days in list must be integers between 0 and 6 (inclusive).'

    route = models.Route(user_id=int(user.id))

    if route_id:
        if type(route_id) is not int:
            return None, 'Route ID must be an integer.'

        route = None

        route = models.Route.query.get(int(route_id))

        if not route:
            return None, 'Route does not exist.'

        if route.user_id != user.id:
            return None, 'Route does not belong to user.'

    else:
        if len(user.routes) >= MAX_ROUTES:
            return None, 'Route limit has been reached.'

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

    db.session.add(route)
    db.session.commit()

    return route, None

def delete_route(user_id, route_id):

    if not user_id:
        return None, 'User ID cannot be blank.'
    if type(user_id) is not int:
        return None, 'User ID must be an integer.'

    user = None

    try:
        user = models.User.query.get(int(user_id))
    except:
        return None, 'Error while trying to find user.'

    if not user:
        return None, 'User does not exist.'

    if not route_id:
        return None, 'Route ID cannot be blank.'
    if type(route_id) is not int:
        return None, 'Route ID must be an integer.'

    route = None

    try:
        route = models.Route.query.get(int(route_id))
    except:
        return None, 'Error while trying to find route.'

    if not route:
        return None, 'Route does not exist.'

    if route.user.id != user.id:
        return None, 'Route does not belong to user.'

    db.session.delete(route)
    db.session.commit()

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
