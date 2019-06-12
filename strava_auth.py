"""strava_auth.py

Felix van Oost 2019

Authenticates the application to the Strava v3 API using OAuth2.
This file requires a Strava client ID and client secret to be stored in Credentials.txt.
"""
import os
import requests
from requests import Request
import time
import webbrowser

CLIENT_INFO_FILE = 'ClientInfo.txt'
TOKENS_FILE = 'Tokens.txt'

# Dictionaries for the Strava client information and tokens
client_info = {}
tokens = {}

def read_client_info_from_file():
    """
    Reads the Strava client information (client ID and secret) from a text file and stores them for local use.
    Returns 0 if the client information is successfully read and stored.
    Returns 1 otherwise.
    """

    return_code = 0

    # Open and parse the client information file
    try:
        with open(CLIENT_INFO_FILE, 'r') as file:
            for line in file:
                if line.startswith('STRAVA_CLIENT_ID ='):       # Locate the client ID
                    client_id = line.split('=')[1]              # Split the line and select the right half (2nd element)
                    client_id = client_id.strip()               # Strip any whitespace from the client ID
                    client_info['id'] = client_id               # Update the client ID in the dictionary

                if line.startswith('STRAVA_CLIENT_SECRET ='):   # Locate the client secret
                    client_secret = line.split('=')[1]          # Split the line and select the right half (2nd element)
                    client_secret = client_secret.strip()       # Strip any whitespace from the client secret
                    client_info['secret'] = client_secret       # Update the client secret in the dictionary
    except IOError:
        print('Error: {} does not exist.'.format(CLIENT_INFO_FILE))
        return_code = 1

    return return_code

def read_tokens_from_file():
    """
    Reads the Strava tokens and expiry time from a text file and stores them for local use.
    Returns 0 if the token information is successfully read and stored.
    Returns 1 otherwise.
    """

    return_code = 0

    try:
        with open(TOKENS_FILE, 'r') as file:
            for line in file:
                if line.startswith('STRAVA_ACCESS_TOKEN ='):        # Locate the access token
                    access_token = line.split('=')[1]               # Split the line and select the right half (2nd element)
                    access_token = access_token.strip()             # Strip any whitespace from the access token
                    tokens['access_token'] = access_token           # Update the access token in the dictionary

                if line.startswith('STRAVA_REFRESH_TOKEN ='):       # Locate the refresh token
                    refresh_token = line.split('=')[1]              # Split the line and select the right half (2nd element)
                    refresh_token = refresh_token.strip()           # Strip any whitespace from the refresh token
                    tokens['refresh_token'] = refresh_token         # Update the refresh token in the dictionary

                if line.startswith('STRAVA_TOKEN_EXPIRY_TIME ='):   # Locate the access token expiry time
                    expiry_time = line.split('=')[1]                # Split the line and select the right half (2nd element)
                    expiry_time = expiry_time.strip()               # Strip any whitespace from the expiry time
                    tokens['expiry_time'] = expiry_time             # Update the expiry time in the dictionary
    except IOError:
        return_code = 1

    return return_code

def write_tokens_to_file():
    """
    Writes the Strava tokens and expiry time to a text file.
    """

    print('Strava: Writing tokens to {}'.format(TOKENS_FILE))

    # Delete the tokens file if it already exists as the tokens have expired
    try:
        os.remove(TOKENS_FILE)
    except OSError:
        pass

    # Write the tokens and expiry time to a new file
    with open(TOKENS_FILE, 'w') as file:
        file.write('STRAVA_ACCESS_TOKEN = {} \n'.format(tokens['access_token']))
        file.write('STRAVA_REFRESH_TOKEN = {} \n'.format(tokens['refresh_token']))
        file.write('STRAVA_TOKEN_EXPIRY_TIME = {} \n'.format(tokens['expiry_time']))

def refresh_expired_tokens():
    """
    Refreshes the access and refresh tokens.
    """

    print('Strava: Refreshing expired tokens')

    base_address = 'https://www.strava.com/oauth/token'
    data = {'client_id': client_info['id'],
            'client_secret': client_info['secret'],
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']}

    # POST the request and parse the JSON response
    refresh_return = requests.post(base_address, data = data).json()

    # Store the new tokens and expiry time in the dictionary
    tokens['access_token'] = refresh_return.get('access_token')
    tokens['refresh_token'] = refresh_return.get('refresh_token')
    tokens['expiry_time'] = refresh_return.get('expires_at')

    # Write the new tokens and expiry time to a text file for the next use
    write_tokens_to_file()

def get_auth_code():
    """
    Gets and returns the authorization code required to obtain the initial access and refresh tokens.
    """
    
    base_address = 'https://www.strava.com/oauth/authorize'
    params = ({'client_id': client_info['id'],
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

    base_address = 'https://www.strava.com/oauth/token'
    data = {'client_id': client_info['id'],
            'client_secret': client_info['secret'],
            'code': auth_code,
            'grant_type': 'authorization_code'}
    
    # POST the request and parse the JSON response
    auth_return = requests.post(base_address, data = data).json()

    # Store the access and refresh tokens in the credentials dictionary
    tokens['access_token'] = auth_return.get('access_token')
    tokens['refresh_token'] = auth_return.get('refresh_token')
    tokens['expiry_time'] = auth_return.get('expires_at')

def get_initial_tokens():
    """
    Gets the initial access and refresh tokens and writes them to a text file.
    """

    print('Strava: Getting initial tokens')

    # Get the authorization code and exchange it against the initial access and refresh tokens
    auth_code = get_auth_code()
    exchange_tokens(auth_code)

    # Write the initial tokens and expiry time to a text file for the next use
    write_tokens_to_file()

def authenticate():
    """
    Authenticates the application to the Strava v3 API using OAuth2.
    Returns an access token for API access.
    """

    print('Strava: Authenticating access to the API')
    
    access_token = 0

    # Read the Strava client information from the corresponding text file
    if read_client_info_from_file() is 0:
        # Read the Strava tokens and expiry time from the corresponding text file
        if read_tokens_from_file() is 0:
            # Check if the access token has expired
            if int(tokens['expiry_time']) <= time.time():
                # Refresh the expired tokens
                refresh_expired_tokens()
        else:
            # Get the initial access and refresh tokens
            get_initial_tokens()
    
        print('Strava: Access to the API authenticated')
        access_token = tokens['access_token']

    return access_token