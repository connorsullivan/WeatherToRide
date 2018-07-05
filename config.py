import os

# Define the base directory for the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Enable protection against *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Enable debug mode
DEBUG = True

# Set the environment to dev (not production)
ENV = 'development'

# Set this to suppress a console warning
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Set the number of application threads
THREADS_PER_PAGE = 2
