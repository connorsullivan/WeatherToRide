
# import sendgrid
# import os
# from sendgrid.helpers.mail import Email, Content, Mail

# from .. import app

# def send(to_address, subject, message):

#     sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])

#     from_address = 'support@weathertoride.com'

#     from_email = Email(from_address)
#     to_email = Email(to_address)
#     subject = subject
#     content = Content("text/html", message)

#     mail = Mail(from_email, subject, to_email, content)

#     response = sg.client.mail.send.post(request_body=mail.get())

#     return [
#         response.status_code,
#         response.body,
#         response.headers
#     ]

# # The subject of the activation e-mail
        # subject = 'Confirm your e-mail address'

        # # The secure token that is linked to this user
        # token = security.ts.dumps(user.email, salt='email-confirm-key')

        # # The complete e-mail confirmation URL for this user
        # confirm_url = url_for(

        #     # The function to call
        #     'confirm_email',

        #     # The token to pass to the function
        #     token=token,

        #     # Return an absolute URL instead of a relative one
        #     _external=True

        # )

        # # The HTML for the activation e-mail
        # html = render_template(

        #     # The template to send
        #     'email/confirm.html', 

        #     # The user that is creating this account
        #     user=user, 

        #     # The parameters to pass to the template
        #     confirm_url=confirm_url

        # )

        # email.send(user.email, subject, html)

        # sms.send(user.phone, 'Thanks for trying my app!')
