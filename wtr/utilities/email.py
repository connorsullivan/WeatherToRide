import sendgrid
import os
from sendgrid.helpers.mail import Email, Content, Mail

from .. import app

def send(to_address, subject, message):

    sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])

    from_address = 'support@weathertoride.com'

    from_email = Email(from_address)
    to_email = Email(to_address)
    subject = subject
    content = Content("text/html", message)

    mail = Mail(from_email, subject, to_email, content)

    response = sg.client.mail.send.post(request_body=mail.get())

    return [
        response.status_code,
        response.body,
        response.headers
    ]
