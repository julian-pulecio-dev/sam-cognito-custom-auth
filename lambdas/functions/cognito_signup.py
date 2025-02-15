import boto3
import json
import os
from models.event import Event

# Replace these values with your actual Cognito pool ID, client ID, and region
user_pool_id = os.environ['UserPoolID']
client_id = os.environ['ClientID']

# Initialize the Cognito Identity Provider client
client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    print('event:', event)
    event = Event(event)
    try:
      response = client.sign_up(
          ClientId=client_id,
          Username=event.form_data['Username'],
          Password=event.form_data['Password']
      )
    except client.exceptions.NotAuthorizedException as e:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotFoundException as e:
        return None, "The username or password is incorrect"
    except Exception as e:
        print(e)
        return None, "Unknown error"
    return response, None