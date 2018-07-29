
# from twilio.rest import Client

# from .. import app

# # Your Account SID from twilio.com/console
# account_sid = app.config['TWILIO_SID']
# # Your Auth Token from twilio.com/console
# auth_token = app.config['TWILIO_AUTH_TOKEN']

# client = Client(account_sid, auth_token)

# def send(to_number, message):

#     message = client.messages.create(
#         to=to_number, 
#         from_=app.config['TWILIO_FROM_NUMBER'],
#         body=message
#     )

#     return message.sid
