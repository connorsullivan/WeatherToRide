
from .. import app

from flask import render_template
from flask_login import current_user

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

# Import the other views from this package
from . import user
from . import location
from . import route
