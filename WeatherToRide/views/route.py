
from .. import app, csrf, db, forms, models

from ..utils import validator

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

import datetime

# Limit how many routes a user can have at one time
MAX_ROUTES = 5

def create_or_update_route(user_id, location_id_1, location_id_2, name, days, route_id=None):

    # Validate the user
    user, error = validator.validate_user(user_id)
    if error:
        return None, error

    # Validate the first location
    location_1, error = validator.validate_location(location_id_1)
    if error:
        return None, error

    if location_1.user != user:
        return None, 'Location 1 does not belong to user.'

    # Validate the second location
    location_2, error = validator.validate_location(location_id_2)
    if error:
        return None, error

    if location_2.user != user:
        return None, 'Location 2 does not belong to user.'

    # Make sure the two locations are different
    if location_1 == location_2:
        return None, 'The two locations must be different.'

    # Validate the route name
    max_length_name = models.Route.name.property.columns[0].type.length
    if not name or type(name) is not str:
        return None, 'Route name must be a non-empty string.'
    if len(name) > max_length_name:
        return None, f'Route name cannot be longer than {max_length_name} characters.'

    # Validate the route days
    if not days:
        return None, 'Days are required.'
    if type(days) is not list:
        return None, 'Days must be a non-empty list of integers [0-6]'
    for day in days:
        if type(day) is not int:
            return None, 'Encountered day in list that was not an integer'
        if day < 0 or day > 6:
            return None, 'Encountered day in list that was outside of allowable range [0-6]'

    # Validate the current route (if updating instead of creating)
    route = None
    if route_id:
        route, error = validator.validate_route(route_id)
        if error:
            return None, error

    # Create a new route if not updating
    if not route:
        if len(user.routes) < MAX_ROUTES:
            route = models.Route(user_id=user.id)
        else:
            return None, 'Route limit has been reached.'

    # Save the new information to this route
    route.location_id_1 = location_1.id
    route.location_id_2 = location_2.id

    route.name = name

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

    # Return the created/updated route
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

    # Delete the route from the database
    db.session.delete(route)
    db.session.commit()

    # Return the deleted route
    return route, None

@app.route('/route/create', methods=['GET', 'POST'])
@login_required
def route_create_view():

    # Check that the user has enough locations
    if len(current_user.locations) < 2:
        flash('You must have at least 2 saved locations to create a route.', 'danger')
        return redirect(url_for('route_view'))

    # Get a RouteForm from forms.py
    form = forms.RouteForm()
    form.location_id_1.choices = [(x.id, x.name) for x in current_user.locations]
    form.location_id_2.choices = [(x.id, x.name) for x in current_user.locations]

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to add the route to the database
        route, error = create_or_update_route(
            user_id=current_user.id, 
            location_id_1=form.location_id_1.data, 
            location_id_2=form.location_id_2.data, 
            name=form.name.data, 
            days=form.days.data
        )

        # Check if the route was created
        if route and not error:
            flash('The route was successfully created!', 'success')
            return redirect(url_for('route_view'))
        else:
            flash(error, 'danger')

    # Return the route form
    return render_template('route/route-form.html', user=current_user, form=form)

@app.route('/api/<key>/route/create', methods=['POST'])
@csrf.exempt
def route_create_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    # Validate the request
    if not request.json:
        abort(400)
    if not 'routeLocation1' in request.json:
        abort(400)
    if not 'routeLocation2' in request.json:
        abort(400)
    if not 'routeName' in request.json:
        abort(400)
    if not 'routeDays' in request.json:
        abort(400)

    # Try to add the route to the database
    route, error = create_or_update_route(
        user_id=user.id, 
        location_id_1=request.json['routeLocation1'], 
        location_id_2=request.json['routeLocation2'], 
        name=request.json['routeName'], 
        days=request.json['routeDays']
    )

    # Check if the route was created
    if route and not error:
        return jsonify({ 'createdRoute': route.serialize() })
    else:
        return jsonify({ 'error': error }), 400

@app.route('/routes')
@login_required
def route_view():
    today = datetime.date.today()
    db_routes = current_user.routes
    routes = []
    for r in db_routes:
        location_1 = models.Location.query.get(r.location_id_1)
        location_2 = models.Location.query.get(r.location_id_2)
        forecast = []
        for i in range(7):
            day = (today + datetime.timedelta(days=i))
            # if the route is active for this day
            if getattr(r, day.strftime('%a').lower()):
                forecast.append({
                    'day': 'Today' if i == 0 else 'Tomorrow' if i == 1 else day.strftime('%A'),
                    'location_1': {
                        'icon': getattr(location_1.forecast, f'day_{i}_icon'),
                        'summary': getattr(location_1.forecast, f'day_{i}_summary'),
                        'recommendation': getattr(location_1.forecast, f'day_{i}_recommendation')
                    },
                    'location_2': {
                        'icon': getattr(location_2.forecast, f'day_{i}_icon'),
                        'summary': getattr(location_2.forecast, f'day_{i}_summary'),
                        'recommendation': getattr(location_2.forecast, f'day_{i}_recommendation')
                    }
                })
        routes.append({
            'id': r.id,
            'name': r.name,
            'location_1_name': location_1.name,
            'location_2_name': location_2.name,
            'forecast': forecast
        })

    # Return the route view
    return render_template('route/routes.html', user=current_user, routes=routes)

@app.route('/api/<key>/routes')
@csrf.exempt
def route_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    length = len(user.routes)
    routes = [r.serialize() for r in user.routes]

    for route in routes:

        # Get the locations for this route
        location1 = models.Location.query.get( route['routeLocation1'] )
        location2 = models.Location.query.get( route['routeLocation2'] )

        # Add the locations to the JSON response
        route['routeLocation1'] = location1.serialize()
        route['routeLocation2'] = location2.serialize()

        # Add the forecasts to the JSON response
        route['routeLocation1']['forecast'] = location1.forecast.serialize()
        route['routeLocation2']['forecast'] = location2.forecast.serialize()

    return jsonify({ 'userId': user.id, 'numberOfRoutes': length, 'routes': routes })

@app.route('/route/update/<int:id>', methods=['GET', 'POST'])
@login_required
def route_update_view(id):

    # Try to find this route in the database
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

    # Create a RouteForm with the current values populated
    form = forms.RouteForm(
        location_id_1=route.location_id_1, 
        location_id_2=route.location_id_2, 
        name=route.name, 
        days=days
    )

    form.location_id_1.choices = [(x.id, x.name) for x in current_user.locations]
    form.location_id_2.choices = [(x.id, x.name) for x in current_user.locations]

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to update the route in the database
        route, error = create_or_update_route(
            user_id=current_user.id, 
            location_id_1=form.location_id_1.data, 
            location_id_2=form.location_id_2.data, 
            name=form.name.data, 
            days=form.days.data, 
            route_id=route.id
        )

        # Check if the route was updated
        if route and not error:
            flash('The route was successfully updated!', 'success')
            return redirect(url_for('route_view'))
        else:
            flash(error, 'danger')

    # Return the route form
    return render_template('route/route-form.html', user=current_user, form=form)

@app.route('/api/<key>/route/update', methods=['POST'])
@csrf.exempt
def route_update_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    # Validate the request
    if not request.json:
        abort(400)
    if not 'routeLocation1' in request.json:
        abort(400)
    if not 'routeLocation2' in request.json:
        abort(400)
    if not 'routeName' in request.json:
        abort(400)
    if not 'routeDays' in request.json:
        abort(400)
    if not 'routeId' in request.json:
        abort(400)

    # Try to update the route in the database
    route, error = create_or_update_route(
        user_id=user.id, 
        location_id_1=request.json['routeLocation1'], 
        location_id_2=request.json['routeLocation2'], 
        name=request.json['routeName'], 
        days=request.json['routeDays'], 
        route_id=request.json['routeId']
    )

    # Check if the route was updated
    if route and not error:
        return jsonify({ 'updatedRoute': route.serialize() })
    else:
        return jsonify({ 'error': error }), 400

@app.route('/route/delete/<int:id>', methods=['POST'])
@login_required
def route_delete_view(id):

    # If a delete request is being submitted
    if request.method == 'POST':

        # Try to delete the route from the database
        route, error = delete_route(current_user.id, id)

        # Check if the route was deleted
        if route and not error:
            flash('The route was successfully deleted!', 'success')
        else:
            flash(error, 'danger')

    # Return the route view
    return redirect(url_for('route_view'))

@app.route('/api/<key>/route/delete', methods=['DELETE'])
@csrf.exempt
def route_delete_api(key):

    # Validate the API key
    user, error = validators.validate_developer(key)
    if error:
        return jsonify({ 'error': error }), 400

    # Check that the request is valid
    if not request.json:
        abort(400)
    if not 'routeId' in request.json:
        abort(400)

    # Try to delete the route from the database
    route, error = delete_route(user.id, request.json['routeId'])

    # Check if the route was deleted
    if error:
        return jsonify({ 'error': error }), 400
    else:
        return jsonify({ 'deletedRoute': route.serialize() })
