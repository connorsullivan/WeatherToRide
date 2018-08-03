
from .. import models

def validate_user(id):
    
    if type(id) is not int:
        return None, 'User ID must be an integer.'

    # Try to find the user in the database
    user = None
    try:
        user = models.User.query.get(id)
    except:
        return None, 'Error while trying to find user.'
    if not user:
        return None, 'User does not exist.'
    else:
        return user, None

def validate_developer(key):

    if type(key) is not str:
        return None, 'API key must be a string.'
    
    # Try to find the developer in the database
    developer = None
    try:
        developer = models.Developer.query.filter_by(key=key).first()
    except:
        return None, 'Error while trying to authenticate API key.'
    if not developer:
        return None, 'The API key is invalid.'
    else:
        return developer.user, None

def validate_location(id):

    if type(id) is not int:
        return None, 'Location ID must be an integer.'

    # Try to find the location in the database
    location = None
    try:
        location = models.Location.query.get(id)
    except:
        return None, 'Error while trying to find location.'
    if not location:
        return None, 'Location does not exist.'
    else:
        return location, None

def validate_route(id):

    if type(id) is not int:
        return None, 'Route ID must be an integer.'

    # Try to find the route in the database
    route = None
    try:
        route = models.Route.query.get(id)
    except:
        return None, 'Error while trying to find route.'
    if not route:
        return None, 'Route does not exist.'
    else:
        return route, None
