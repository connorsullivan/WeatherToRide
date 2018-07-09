from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)

# Load config.py in project root
app.config.from_object('config')

# Load config.py in project /instance
app.config.from_pyfile('config.py')

# Flask-SQLAlchemy
db = SQLAlchemy(app)

# Flask-Login
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = 'Please log in first.'
lm.login_message_category = 'danger'

# Views for handling routes
from . import views
