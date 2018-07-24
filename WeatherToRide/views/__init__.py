
from .. import app

from ..forms import DeleteForm
from ..models import Location, Route, User

from flask import render_template
from flask_login import current_user, login_required

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
    form = DeleteForm()

    # Locations for this user
    locations = Location.query.filter_by(user_id=current_user.id)

    # Routes for this user
    routes = Route.query.filter_by(user_id=current_user.id)

    return render_template('dashboard.html', user=current_user, form=form, locations=locations, routes=routes)

@app.route('/users')
@login_required
def show_all_users():
    users = User.query.order_by(User.id).all()
    return render_template('users.html', user=current_user, users=users)

from . import auth
from . import locations
from . import routes
