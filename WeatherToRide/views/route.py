
from .. import app, db, forms, models

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

# Limit how many routes a user can have at one time
MAX_ROUTES = 3

def create_or_update_route(user_id, name, start, final, time, days, route_id=None):

    # Validate the user
    if not user_id:
        return None, 'User ID cannot be blank.'
    if type(user_id) is not int:
        return None, 'User ID must be an integer.'

    # Find the user in the database
    user = None

    try:
        user = models.User.query.get(int(user_id))
    except:
        return None, 'Error while trying to find user.'

    if not user:
        return None, 'User does not exist.'

    # Validate the route name
    max_length_name = models.Route.name.property.columns[0].type.length

    if not name:
        return None, 'Route name cannot be blank.'
    if type(name) is not str:
        return None, 'Route name must be a string.'
    if len(name) > max_length_name:
        return None, f'Route name cannot be longer than {max_length_name} characters.'

    # Validate the route starting location
    if not start:
        return None, 'Starting location ID is required.'
    if type(start) is not int:
        return None, 'Starting location ID must be an integer.'

    start_location = None

    try:
        start_location = models.Location.query.get(int(start))
    except:
        return None, 'Error while trying to find starting location.'

    if not start_location:
        return None, 'Starting location does not exist.'

    if start_location.user_id != user.id:
        return None, 'Starting location does not belong to user.'

    # Validate the route ending location
    if not final:
        return None, 'Ending location ID is required.'
    if type(final) is not int:
        return None, 'Ending location ID must be an integer.'

    final_location = None

    try:
        final_location = models.Location.query.get(int(final))
    except:
        return None, 'Error while trying to find ending location.'

    if not final_location:
        return None, 'Ending location does not exist.'

    if final_location.user_id != user.id:
        return None, 'Ending location does not belong to user.'

    # Create a new location
    location = models.Location(user_id=int(user.id))

    # Validate the location (if one already exists)
    if location_id:
        if type(location_id) is not int:
            return None, 'Location ID must be an integer.'

        location = None

        location = models.Location.query.get(int(location_id))

        if not location:
            return None, 'Location does not exist.'

        if location.user_id != user.id:
            return None, 'Location does not belong to user.'

    # Check that the user doesn't have too many locations
    else:
        if len(user.locations) >= MAX_LOCATIONS:
            return None, 'Location limit has been reached.'

    # Get the coordinates from the address
    lat, lng = geocode.get_coordinates(str(address))

    if not lat or not lng:
        return None, 'Address could not be located.'

    # Add the information to the route
    route.name = name
    route.start = start
    route.final = final
    route.time = time
    route.days = days

    # Add the route to the database
    db.session.add(route)
    db.session.commit()

    return route, None

@app.route('/route/create', methods=['GET', 'POST'])
@login_required
def create_route():

    # Check that the user has enough locations to make a route
    if len(current_user.locations) < 2:
        flash('You must have at least 2 saved locations before creating a route.', 'danger')
        return redirect(url_for('dashboard'))

    # Get a RouteForm from forms.py
    form = forms.RouteForm()

    # Get the user's locations
    locations = models.Location.query.filter_by(user_id=current_user.id)

    form.start.choices = [(x.id, x.name) for x in locations]
    form.final.choices = [(x.id, x.name) for x in locations]

    # If a valid RouteForm was submitted
    if form.validate_on_submit():

        # Get the user's routes
        routes = models.Route.query.filter_by(user_id=current_user.id).all()

        # If the user doesn't have too many routes
        if len(routes) < MAX_ROUTES:

            # Create a new route in the database
            route = models.Route(user_id=current_user.id)

            route.name = form.name.data
            route.start = form.start.data
            route.final = form.final.data
            route.time = form.time.data

            days = form.days.data

            for day in days:
                if day == 0:
                    route.mon = True
                elif day == 1:
                    route.tue = True
                elif day == 2:
                    route.wed = True
                elif day == 3:
                    route.thu = True
                elif day == 4:
                    route.fri = True
                elif day == 5:
                    route.sat = True
                elif day == 6:
                    route.sun = True

            # Add the route to the database
            db.session.add(route)
            db.session.commit()

            # Flash a confirmation message to the user
            flash('The route was successfully added!', 'success')

            # Redirect to the dashboard
            return redirect(url_for('dashboard'))

        # If the user has too many routes
        else:
            flash('Please delete a route before trying to add another.', 'danger')

    # Return the route page
    return render_template('route/route.html', user=current_user, form=form)

@app.route('/route/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_route(id):

    # Get the target route from the database
    route = models.Route.query.get(int(id))

    # Create a RouteForm with the pre-existing values already populated
    form = forms.RouteForm(name=route.name, start=route.start, final=route.final, time=route.time)

    # Get the user's locations
    locations = models.Location.query.filter_by(user_id=current_user.id)

    form.start.choices = [(x.id, x.name) for x in locations]
    form.final.choices = [(x.id, x.name) for x in locations]

    # If a valid RouteForm was submitted
    if form.validate_on_submit():

        # Update the route in the database
        route.name = form.name.data
        route.start = form.start.data
        route.final = form.final.data
        route.time = form.time.data

        # Save the changes to the database
        db.session.commit()

        # Flash a confirmation message to the user
        flash('The route was successfully added!', 'success')

        # Redirect to the dashboard
        return redirect(url_for('dashboard'))

    # Return the route page
    return render_template('route/route.html', user=current_user, form=form)

@app.route('/route/delete/<int:id>', methods=['POST'])
@login_required
def delete_route(id):

    # Get a SubmitForm from forms.py
    form = forms.SubmitForm()

    # If a valid SubmitForm was submitted
    if form.validate_on_submit():

        # This will hold the route to be deleted
        toDelete = None

        # Get the user's routes
        routes = models.Route.query.filter_by(user_id=current_user.id)

        # Find the route to be deleted from the user's routes
        for route in routes:
            if route.id == id:
                toDelete = route
                break

        # If a matching route was found
        if toDelete:

            # Delete the route from the database
            db.session.delete(route)
            db.session.commit()

            # Flash a confirmation message to the user
            flash('The route was deleted.', 'success')

        # If no matching route was found
        else:

            # Flash an error message to the user
            flash('You do not have any routes with that ID.', 'danger')

    # Redirect to the dashboard
    return redirect(url_for('dashboard'))
