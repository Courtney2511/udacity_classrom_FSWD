from twilio.rest import TwilioRestClient

account_sid = "AC1b8c1520abba3af7a62248cbd53efcdf" # Your Account SID from www.twilio.com/console
auth_token  = "2a87b8dc577a09b09606e07b3891accf"  # Your Auth Token from www.twilio.com/console

client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(body="Hello from Python",
    to="+14167259954",    # Replace with your phone number
    from_="+16475589919") # Replace with your Twilio number

print(message.sid)
