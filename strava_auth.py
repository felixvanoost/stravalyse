"""strava_auth.py

Authenticates access to the Strava v3 API using OAuth2.

Felix van Oost 2024
"""

# Standard library
import os
import pathlib
import time
import webbrowser

# Third-party
from dotenv import load_dotenv
from stravalib import Client
from stravalib.protocol import AccessInfo


def _read_tokens_from_file(file_path: pathlib.Path) -> AccessInfo:
    """
    Read the Strava authentication tokens and expiry time from a text file.

    Arguments:
    file_path - The path of the file to read the tokens from.

    Return:
    A dictionary containing the authentication tokens and expiry time.
    An empty dictionary if the file cannot be read from successfully.
    """

    print(f"[Strava]: Reading authentication tokens from '{file_path}'")

    tokens: AccessInfo = {}

    try:
        with file_path.open(mode='r') as file:
            for line in file:
                if line.startswith('STRAVA_ACCESS_TOKEN ='):
                    tokens['access_token'] = line.split('=')[1].strip()
                elif line.startswith('STRAVA_REFRESH_TOKEN ='):
                    tokens['refresh_token'] = line.split('=')[1].strip()
                elif line.startswith('STRAVA_TOKEN_EXPIRY ='):
                    tokens['expires_at'] = line.split('=')[1].strip()
                else:
                    pass
    except IOError:
        print('[Strava]: No authentication tokens found')

    return tokens


def _write_tokens_to_file(file_path: pathlib.Path, tokens: AccessInfo):
    """
    Write the Strava authentication tokens to a text file.

    Arguments:
    file_path - The path of the file to write the tokens to.
    tokens - The tokens to write to the file.
    """

    print(f"[Strava]: Writing authentication tokens to '{file_path}'")

    # Delete the file to remove any expired tokens
    try:
        file_path.unlink()
    except OSError:
        pass

    # Write the tokens to a new file
    with file_path.open(mode='w') as file:
        file.write(f'STRAVA_ACCESS_TOKEN = {tokens['access_token']}\n')
        file.write(f'STRAVA_REFRESH_TOKEN = {tokens['refresh_token']}\n')
        file.write(f'STRAVA_TOKEN_EXPIRY = {tokens['expires_at']}\n')


def _get_initial_tokens(client: Client, client_id: int, client_secret: str) -> AccessInfo:
    """
        Get and return the initial Strava authentication tokens.

        Arguments:
        client_info - A dictionary containing the client ID and secret.

        Return:
        A dictionary containing the initial authentication tokens and expiry
        time.
        """

    print('[Strava]: Getting initial authentication tokens')

    # Generate the authorization URL and open it in a browser
    url = client.authorization_url(client_id=client_id,
                                   redirect_uri='http://localhost')
    webbrowser.open(url)

    # TODO: Get the authorization code back from the response automatically. Currently, the code
    # must be manually copied from the URL response in the browser window.
    auth_code = str(input("Enter authorization code: "))

    # Exchange the authorization code for the initial set of tokens
    token_response: AccessInfo = client.exchange_code_for_token(client_id=client_id,
                                                                client_secret=client_secret,
                                                                code=auth_code)

    return token_response


def get_access_token(file_path: pathlib.Path) -> str:
    """
    Obtain and return an OAuth2 access token for the Strava API.

    Arguments:
    file_path - The path of the file to store the access tokens to.

    Return:
    The access token as a string if access to the API is successfully
    authenticated.
    None if an access token cannot be generated.
    """

    load_dotenv()

    client_id = os.environ.get('STRAVA_CLIENT_ID')
    client_secret = os.environ.get('STRAVA_CLIENT_SECRET')

    client = Client()

    # Read the authentication tokens and expiry time from the file
    existing_tokens = _read_tokens_from_file(file_path)
    if existing_tokens:
        # Refresh the tokens if they have expired and write the new tokens to the file
        if int(existing_tokens['expires_at']) <= time.time():
            new_tokens = client.refresh_access_token(client_id=client_id,
                                                     client_secret=client_secret,
                                                     refresh_token=existing_tokens['refresh_token'])
            _write_tokens_to_file(file_path, new_tokens)
            access_token = new_tokens['access_token']
        else:
            access_token = existing_tokens['access_token']
    else:
        # Get the initial authentication tokens and write them to the file
        initial_tokens = _get_initial_tokens(client, client_id, client_secret)
        _write_tokens_to_file(file_path, initial_tokens)
        access_token = initial_tokens['access_token']

    print('[Strava]: Access to the API authenticated')

    return access_token
