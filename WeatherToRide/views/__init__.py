
from .. import app, forms, models

from ..utils import weather

from flask import render_template
from flask_login import current_user, login_required

import datetime

# How old can forecasts be before needing to be refreshed?
max_forecast_age = datetime.timedelta(seconds=900)

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

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
            if forecast_age > max_forecast_age:
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

@app.route('/routes')
@login_required
def route_dashboard():

    # Get a SubmitForm from forms.py
    form = forms.SubmitForm()

    # Get this user's routes
    rs = current_user.routes

    routes = []
    for i, r in enumerate(rs):
        routes.append({ 
            'id': r.id, 
            'name': r.name, 
            'location_1': models.Location.query.get(int(r.location_id_1)), 
            'location_2': models.Location.query.get(int(r.location_id_2)), 
            'days': [] 
        })

        if r.mon:
            routes[i]['days'].append('Mondays')
        if r.tue:
            routes[i]['days'].append('Tuesdays')
        if r.wed:
            routes[i]['days'].append('Wednesdays')
        if r.thu:
            routes[i]['days'].append('Thursdays')
        if r.fri:
            routes[i]['days'].append('Fridays')
        if r.sat:
            routes[i]['days'].append('Saturdays')
        if r.sun:
            routes[i]['days'].append('Sundays')

    # Return the route dashboard page
    return render_template('routes.html', user=current_user, form=form, routes=routes)

# Import the other views from this package
from . import user
from . import location
from . import route
