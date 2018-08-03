
# Code snippet from: https://sendgrid.com/

from .. import app

import sendgrid

from sendgrid.helpers.mail import *

def send(to_address, subject, message):

    # Create a SendGrid client
    sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_KEY'])

    # Get the information for this e-mail
    from_email = Email('support@WeatherToRide.com')
    to_email = Email(to_address)
    subject = subject
    content = Content("text/html", message)

    # Create the e-mail
    mail = Mail(from_email, subject, to_email, content)

    # Send the e-mail and return the response
    return sg.client.mail.send.post(request_body=mail.get())
