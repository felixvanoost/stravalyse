"""strava_auth.py

Felix van Oost 2019

Authenticates the application to the Strava v3 API using OAuth2.
This file requires a Strava client ID and client secret to be stored in Credentials.txt.
"""
import requests
from requests import Request
import webbrowser

FILE_CREDENTIALS = 'Credentials.txt'

# Dictionary for the Strava client credentials
strava_credentials = {}

def read_strava_credentials():
    """
    Reads the Strava client credentials (client ID and secret) from the text file and stores
    them in a dictionary.
    """

    # Open and parse the credentials file
    with open(FILE_CREDENTIALS, 'r') as file:
        for line in file:
            if line.startswith('STRAVA_CLIENT_ID ='):               # Locate the client ID
                client_id = line.split('=')[1]                      # Split the line and select the right half (2nd element)
                client_id = client_id.strip()                       # Strip any whitespace from the client ID
                strava_credentials['client_id'] = client_id         # Update the client ID in the credentials dictionary

            if line.startswith('STRAVA_CLIENT_SECRET ='):           # Locate the client secret
                client_secret = line.split('=')[1]                  # Split the line and select the right half (2nd element)
                client_secret = client_secret.strip()               # Strip any whitespace from the client secret
                strava_credentials['client_secret'] = client_secret # Update the client secret in the credentials dictionary

def get_initial_auth_code():
    """
    Gets and returns the initial authorization code required to obtain the access and refresh tokens.
    """

    print('Strava: Getting initial authorization code')
    
    base_address = 'https://www.strava.com/oauth/authorize'
    params = ({'client_id': strava_credentials['client_id'],
               'redirect_uri': 'http://localhost',
               'response_type': 'code',
               'approval_prompt': 'auto',
               'scope': 'activity:read_all'})

    # Prepare the authorization code HTTP request and open it in a browser window
    authorization_request = Request('GET', base_address, params = params).prepare()
    webbrowser.open(authorization_request.url)

    """
    TODO: Get the authorization code back from the response automatically. Currently, the code must be copied from the URL
          response in the browser window.
    """
    # Store the authorization code in the credentials dictionary
    strava_credentials['auth_code'] = input("Authorization code: ")

def exchange_tokens():
    """
    Exchanges the authorization code against access and refresh tokens.
    """

    print('Strava: Getting access and refresh tokens')

    base_address = 'https://www.strava.com/oauth/token'
    data = {'client_id': strava_credentials['client_id'],
            'client_secret': strava_credentials['client_secret'],
            'code': strava_credentials['auth_code'],
            'grant_type': 'authorization_code'}
    
    auth_return = requests.post(base_address, data = data).json()

    # Store the access and refresh tokens in the credentials dictionary
    strava_credentials['access_token'] = auth_return.get('access_token')
    strava_credentials['refresh_token'] = auth_return.get('refresh_token')

def authenticate():
    """
    Authenticates the application to the Strava v3 API using OAuth2
    """
    
    # Read the Strava credentials from the text file
    read_strava_credentials()

    # Get the initial authorization code required to obtain the access and refresh tokens
    get_initial_auth_code()

    # Exchange the authorization code against the access and refresh tokens
    exchange_tokens()