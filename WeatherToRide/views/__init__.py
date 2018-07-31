
from .. import app, forms, models

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

    # Get an instance of the SubmitForm from forms.py
    form = forms.SubmitForm()

    # Get this user's locations
    locations = models.Location.query.filter_by(user_id=current_user.id)

    # Get this user's routes
    routes = models.Route.query.filter_by(user_id=current_user.id)

    # Return the dashboard page
    return render_template('dashboard.html', 
        user=current_user, 
        form=form, 
        locations=locations, 
        routes=routes
    )

@app.route('/users')
@login_required
def show_all_users():

    # Get all of the users from the database
    users = models.User.query.order_by(models.User.id).all()

    # Return the users page
    return render_template('users.html', user=current_user, users=users)

# Import the other views from this package
from . import auth
from . import location
from . import route
