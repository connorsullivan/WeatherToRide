
import os

# Define the base directory for the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Enable protection against *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

''' 
This is the default DB connection string for SQLAlchemy

For added security, change the MySQL password for user 'weather' 
    and move this setting into the instance folder.
'''
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://weather:password@localhost:3306/WeatherToRide'

# Set this to suppress a console warning
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Set the number of application threads
THREADS_PER_PAGE = 2
