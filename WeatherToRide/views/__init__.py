
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

@app.route('/dashboard')
@login_required
def dashboard():

    # Get an instance of the SubmitForm from forms.py
    form = forms.SubmitForm()

    # Get this user's locations
    locations = models.Location.query.filter_by(user_id=current_user.id)

    # Update the forecasting information if needed
    now = datetime.datetime.now()

    for location in locations:
        if location.forecast:
            forecast_age = now - location.forecast.updated_at
            if forecast_age > max_forecast_age:
                weather.update_forecast(location)
        else:
            weather.update_forecast(location)

    # Get this user's routes
    rs = models.Route.query.filter_by(user_id=current_user.id)
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

    today = now.date()

    # Return the dashboard page
    return render_template('dashboard.html', 
        user=current_user, 
        form=form, 
        locations=locations, 
        routes=routes, 
        day_2=(today + datetime.timedelta(days=2)).strftime('%A'), 
        day_3=(today + datetime.timedelta(days=3)).strftime('%A'), 
        day_4=(today + datetime.timedelta(days=4)).strftime('%A'), 
        day_5=(today + datetime.timedelta(days=5)).strftime('%A'), 
        day_6=(today + datetime.timedelta(days=6)).strftime('%A'), 
        day_7=(today + datetime.timedelta(days=7)).strftime('%A') 
    )

# Import the other views from this package
from . import auth
from . import location
from . import route
