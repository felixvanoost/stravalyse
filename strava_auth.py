"""strava_auth.py

Felix van Oost 2019

Authenticates the application to the Strava v3 API using OAuth2.
This file requires a Strava client ID and client secret to be stored in Credentials.txt.
"""
import os
import requests
from requests import Request
import webbrowser

CREDENTIALS_FILE = 'Credentials.txt'
REFRESH_TOKEN_FILE = 'RefreshToken.txt'

# Dictionary for the Strava client credentials
strava_credentials = {}

def read_strava_credentials():
    """
    Reads the Strava client credentials (client ID and secret) from a text file and stores
    them in a dictionary.
    """

    # Open and parse the credentials file
    with open(CREDENTIALS_FILE, 'r') as file:
        for line in file:
            if line.startswith('STRAVA_CLIENT_ID ='):               # Locate the client ID
                client_id = line.split('=')[1]                      # Split the line and select the right half (2nd element)
                client_id = client_id.strip()                       # Strip any whitespace from the client ID
                strava_credentials['client_id'] = client_id         # Update the client ID in the credentials dictionary

            if line.startswith('STRAVA_CLIENT_SECRET ='):           # Locate the client secret
                client_secret = line.split('=')[1]                  # Split the line and select the right half (2nd element)
                client_secret = client_secret.strip()               # Strip any whitespace from the client secret
                strava_credentials['client_secret'] = client_secret # Update the client secret in the credentials dictionary

def get_auth_code():
    """
    Gets and returns the authorization code required to obtain the initial access and refresh tokens.
    """

    print('Strava: Getting authorization code')
    
    base_address = 'https://www.strava.com/oauth/authorize'
    params = ({'client_id': strava_credentials['client_id'],
               'redirect_uri': 'http://localhost',
               'response_type': 'code',
               'approval_prompt': 'auto',
               'scope': 'activity:read_all'})

    # Prepare the authorization code GET request and open it in a browser window
    authorization_request = Request('GET', base_address, params = params).prepare()
    webbrowser.open(authorization_request.url)

    """
    TODO: Get the authorization code back from the response automatically. Currently, the code must be copied from the URL
          response in the browser window.
    """
    auth_code = input("Authorization code: ")

    return auth_code

def exchange_tokens(auth_code):
    """
    Exchanges the authorization code against the initial access and refresh tokens.
    """

    print('Strava: Getting initial access and refresh tokens')

    base_address = 'https://www.strava.com/oauth/token'
    data = {'client_id': strava_credentials['client_id'],
            'client_secret': strava_credentials['client_secret'],
            'code': auth_code,
            'grant_type': 'authorization_code'}
    
    # POST the request and parse the JSON response
    auth_return = requests.post(base_address, data = data).json()

    # Store the access and refresh tokens in the credentials dictionary
    strava_credentials['access_token'] = auth_return.get('access_token')
    strava_credentials['refresh_token'] = auth_return.get('refresh_token')
    strava_credentials['token_expiry_time'] = auth_return.get('expires_at')

def get_initial_tokens():
    """
    Gets the initial access and refresh tokens.
    """
    # Get the authorization code and exchange it against the initial access and refresh tokens
    auth_code = get_auth_code()
    exchange_tokens(auth_code)

    # Store the initial refresh token in a text file for the next use
    write_refresh_token()

def refresh_expired_access_token():
    """
    Refreshes the access token.
    """

    print('Strava: Refreshing access token')

    base_address = 'https://www.strava.com/oauth/token'
    data = {'client_id': strava_credentials['client_id'],
            'client_secret': strava_credentials['client_secret'],
            'grant_type': 'refresh_token',
            'refresh_token': strava_credentials['refresh_token']}

    # POST the request and parse the JSON response
    refresh_return = requests.post(base_address, data = data).json()

    # Store the new access and refresh tokens in the credentials dictionary
    strava_credentials['access_token'] = refresh_return.get('access_token')
    strava_credentials['refresh_token'] = refresh_return.get('refresh_token')
    strava_credentials['token_expiry_time'] = refresh_return.get('expires_at')

def authenticate():
    """
    Authenticates the application to the Strava v3 API using OAuth2
    """
    
    # Read the Strava credentials from the text file
    read_strava_credentials()

    # Get the initial access and refresh tokens
    get_initial_tokens()