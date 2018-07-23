
from .. import app

from ..forms import DeleteForm
from ..models import User

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
    form = DeleteForm()
    return render_template('dashboard.html', user=current_user, form=form)

@app.route('/users')
@login_required
def show_all_users():
    users = User.query.order_by(User.id).all()
    return render_template('users.html', user=current_user, users=users)

from . import auth
from . import locations
