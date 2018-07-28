
from .. import app

from ..forms import *
from ..models import *

from flask import render_template
from flask_login import current_user, login_required

import sys

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/about')
def about():
    return render_template('about.html', user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():

    # Form for deleting locations and routes
    form = SubmitForm()

    # Locations for this user
    locations = Location.query.filter_by(user_id=current_user.id)
    location_ids = [l.id for l in locations]

    # Routes for this user
    routes = Route.query.filter_by(user_id=current_user.id)

    # Weather for this user
    forecasts = Weather.query.filter( Weather.location_id.in_( location_ids )).all()

    return render_template('dashboard.html', user=current_user, form=form, locations=locations, routes=routes, forecasts=forecasts)

@app.route('/users')
@login_required
def show_all_users():
    users = User.query.order_by(User.id).all()
    return render_template('users.html', user=current_user, users=users)

@app.route('/post', methods=['POST'])
def post_test():

    form = RouteForm()

    form.start.choices = [(c.id, c.name) for c in Location.query.filter_by(user_id=current_user.id)]
    form.final.choices = [(c.id, c.name) for c in Location.query.filter_by(user_id=current_user.id)]

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # Combine the collected time with today's date
        today = datetime.date.today()
        time = datetime.datetime.combine(today, form.time.data)

        resp = ''

        for day in form.days.data:
            resp += str(day) + ' ... '

        return resp

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return render_template('route/route.html', user=current_user, form=form)

from . import auth
from . import location
from . import route
