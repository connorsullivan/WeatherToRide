
from .. import models

def validate_user(user_id):
    
    # Validate the input type
    if not user_id:
        return None, 'User ID cannot be blank.'
    if type(user_id) is not int:
        return None, 'User ID must be an integer.'

    # Try to find the user in the database
    user = None

    try:
        user = models.User.query.get(int(user_id))
    except:
        return None, 'Error while trying to find user.'

    if not user:
        return None, 'User does not exist.'
    else:
        return user, None

def validate_location(location_id):

    # Validate the input type
    if not location_id:
        return None, 'Location ID cannot be blank.'
    if type(location_id) is not int:
        return None, 'Location ID must be an integer.'

    # Try to find the user in the database
    location = None

    try:
        location = models.Location.query.get(int(location_id))
    except:
        return None, 'Error while trying to find location.'

    if not location:
        return None, 'Location does not exist.'
    else:
        return location, None

def validate_route(route_id):

    # Validate the input type
    if not route_id:
        return None, 'Route ID cannot be blank.'
    if type(route_id) is not int:
        return None, 'Route ID must be an integer.'

    # Try to find the user in the database
    route = None

    try:
        route = models.Route.query.get(int(route_id))
    except:
        return None, 'Error while trying to find route.'

    if not route:
        return None, 'Route does not exist.'
    else:
        return route, None
