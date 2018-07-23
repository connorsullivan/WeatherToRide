
from flask import Flask, redirect, request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, instance_relative_config=True)

# Load config.py in project root
app.config.from_object('config')

# Load config.py in project /instance
app.config.from_pyfile('config.py')

# Reform '/route/' requests to '/route'
@app.before_request
def clear_trailing():
    rp = request.path
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])

# 404 Handler
@app.errorhandler(404)
def page_not_found(e):
    return "The page you're looking for cannot be found!", 404

# Enable global CSRF protection for this app
csrf = CSRFProtect(app)

# Flask-SQLAlchemy
db = SQLAlchemy(app)

# Flask-Login
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = 'Please log in first.'
lm.login_message_category = 'danger'

# Import the User model
from .models import User

# Tell Flask-Login how to load users from the database
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

# Routing logic is stored in views package
from .views import *
