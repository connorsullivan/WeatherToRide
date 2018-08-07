
# Adapted from https://sendgrid.com/

from .. import app, db, models

import datetime
import sendgrid

from sendgrid.helpers.mail import *

API_NAME = 'SendGrid'
MAX_DAILY_CALLS = 50

def send(to_address, subject, message):

    # Check for the API key
    try:
        sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_KEY'])
    except:
        return None, 'The e-mail API key is not configured.'

    # Get the current date/time
    now = datetime.datetime.now()

    # Get the entry for this API from the database
    status = models.API.query.filter_by(name=API_NAME).first()

    # If there isn't an entry for this API yet
    if not status:
        status = models.API(name=API_NAME)
        status.calls_today = 0
        status.calls_total = 0
        status.last_reset = now
        db.session.add(status)
        db.session.commit()

    # Check if the API call limit needs to be refreshed
    if now.date() > status.last_reset.date():
        status.calls_today = 0
        status.last_reset = now
        db.session.add(status)
        db.session.commit()

    # Check if the API has reached its call limit for today
    if status.calls_today < MAX_DAILY_CALLS:
        status.calls_today += 1
        status.calls_total += 1
        db.session.add(status)
        db.session.commit()
    else:
        return None, 'The e-mail service has reached capacity for today.'

    # Get the information for this e-mail
    from_email = Email('support@WeatherToRide.com')
    to_email = Email(to_address)
    subject = subject
    content = Content("text/html", message)

    # Create the e-mail
    mail = Mail(from_email, subject, to_email, content)

    # Send the e-mail and return the response
    return sg.client.mail.send.post(request_body=mail.get()), None
