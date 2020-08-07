"""strava_auth.py

Authenticates access to the Strava v3 API using OAuth2.

Functions:
get_access_token()

Felix van Oost 2019
"""

# Standard library
import os
import time
import webbrowser
import sys

# Third-party
import requests
from requests import Request


def _read_tokens_from_file(file_path: str) -> dict:
    """
    Read the authentication tokens and expiry time from a text file and
    return them as a dictionary.

    Arguments:
    file_path - The path of the file to read the tokens from.

    Return:
    A dictionary containing the authentication tokens and expiry time.
    An empty dictionary if the file cannot be read from successfully.
    """

    print('Strava: Reading authentication tokens from {}'.format(file_path))

    tokens = {}

    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('STRAVA_ACCESS_TOKEN ='):
                    tokens['access_token'] = line.split('=')[1].strip()
                elif line.startswith('STRAVA_REFRESH_TOKEN ='):
                    tokens['refresh_token'] = line.split('=')[1].strip()
                elif line.startswith('STRAVA_TOKEN_EXPIRY_TIME ='):
                    tokens['expiry_time'] = line.split('=')[1].strip()
                else:
                    pass
    except IOError:
        print('Strava: No authentication tokens found')

    return tokens


def _write_tokens_to_file(file_path: str, tokens: dict):
    """
    Write the authentication tokens and expiry time to a text file.

    Arguments:
    file_path - The path of the file to write the tokens to.
    tokens - A dictionary containing the authentication tokens and
             expiry time to write to the file.
    """

    print('Strava: Writing authentication tokens to {}'.format(file_path))

    # Delete the tokens file to remove any expired tokens
    try:
        os.remove(file_path)
    except OSError:
        pass

    # Write the tokens and expiry time to a new file
    with open(file_path, 'w') as file:
        file.write('STRAVA_ACCESS_TOKEN = {}\n'.format(tokens['access_token']))
        file.write('STRAVA_REFRESH_TOKEN = {}\n'.format(tokens['refresh_token']))
        file.write('STRAVA_TOKEN_EXPIRY_TIME = {}\n'.format(tokens['expiry_time']))


def _refresh_expired_tokens(client_info: dict, expired_tokens: dict) -> dict:
    """
    Refresh the access and refresh tokens and return them as a
    dictionary.

    Arguments:
    client_info - A dictionary containing the client ID and secret.
    expired_tokens - A dictionary containing the expired authentication
                     tokens and expiry time.

    Return:
    A dictionary containing the new authentication tokens and expiry
    time.
    """

    print('Strava: Refreshing expired authentication tokens')

    base_address = 'https://www.strava.com/oauth/token'
    data = {'client_id': client_info['id'],
            'client_secret': client_info['secret'],
            'grant_type': 'refresh_token',
            'refresh_token': expired_tokens['refresh_token']}

    # POST the request and parse the JSON response
    refresh_return = requests.post(base_address, data=data).json()

    # Store the new tokens and expiry time in the dictionary
    new_tokens = {}
    new_tokens['access_token'] = refresh_return.get('access_token')
    new_tokens['refresh_token'] = refresh_return.get('refresh_token')
    new_tokens['expiry_time'] = refresh_return.get('expires_at')

    return new_tokens


def _get_auth_code(client_info: dict) -> str:
    """
    Get and return the authorization code required to obtain the initial
    authentication tokens.

    Arguments:
    client_info - A dictionary containing the client ID and secret.

    Return:
    The authorization code as a string.
    """

    base_address = 'https://www.strava.com/oauth/authorize'
    params = ({'client_id': client_info['id'],
               'redirect_uri': 'http://localhost',
               'response_type': 'code',
               'approval_prompt': 'auto',
               'scope': 'activity:read_all'})

    # Prepare the authorization code GET request and open it in a
    # browser window
    authorization_request = Request('GET', base_address, params=params).prepare()
    webbrowser.open(authorization_request.url)


    # TODO: Get the authorization code back from the response
    # automatically. Currently, the code must be manually copied from
    # the URL response in the browser window.
    auth_code = str(input("Enter authorization code: "))

    return auth_code


def _exchange_tokens(client_info: dict, auth_code: str) -> dict:
    """
    Exchange the authorization code against the initial authentication
    tokens.

    Arguments:
    client_info - A dictionary containing the client ID and secret.
    auth_code - The authorization code as a string.

    Return:
    A dictionary containing the initial authentication tokens and expiry
    time.
    """

    base_address = 'https://www.strava.com/oauth/token'
    data = {'client_id': client_info['id'],
            'client_secret': client_info['secret'],
            'code': auth_code,
            'grant_type': 'authorization_code'}

    # POST the request and parse the JSON response
    auth_return = requests.post(base_address, data=data).json()

    # Store the access and refresh tokens in the credentials dictionary
    tokens = {}
    tokens['access_token'] = auth_return.get('access_token')
    tokens['refresh_token'] = auth_return.get('refresh_token')
    tokens['expiry_time'] = auth_return.get('expires_at')

    return tokens


def _get_initial_tokens(client_info: dict) -> dict:
    """
    Get and return the initial authentication tokens.

    Arguments:
    client_info - A dictionary containing the client ID and secret.

    Return:
    A dictionary containing the initial authentication tokens and expiry
    time.
    """

    print('Strava: Getting initial authentication tokens')

    # Get the authorization code and exchange it against the initial
    # access and refresh tokens
    auth_code = _get_auth_code(client_info)
    tokens = _exchange_tokens(client_info, auth_code)

    return tokens


def get_access_token(file_path: str) -> str:
    """
    Obtain and return an OAuth2 access token for the Strava v3 API.

    Arguments:
    file_path - The path of the file to store the access tokens to.

    Return:
    The access token as a string if access to the API is successfully
    authenticated.
    None if an access token cannot be generated.
    """

    client_info = {}

    # Store the STRAVA_CLIENT_ID environment variable
    try:
        client_info['id'] = os.environ['STRAVA_CLIENT_ID']
    except KeyError:
        sys.exit('ERROR: Add STRAVA_CLIENT_ID to the list of environment variables')

    # Store the STRAVA_CLIENT_SECRET environment variable
    try:
        client_info['secret'] = os.environ['STRAVA_CLIENT_SECRET']
    except KeyError:
        sys.exit('ERROR: Add STRAVA_CLIENT_SECRET to the list of environment variables')

    # Read the authentication tokens and expiry time from the file
    tokens = _read_tokens_from_file(file_path)
    if tokens:
        # Refresh the tokens if the access token has expired and write
        # them to the file
        if int(tokens['expiry_time']) <= time.time():
            tokens = _refresh_expired_tokens(client_info, tokens)
            _write_tokens_to_file(file_path, tokens)
    else:
        # Get the initial authentication tokens and write them to the
        # file
        tokens = _get_initial_tokens(client_info)
        _write_tokens_to_file(file_path, tokens)

    print('Strava: Access to the API authenticated')
    access_token = str(tokens['access_token'])

    return access_token
