"""strava_auth.py

Felix van Oost 2019

Authenticates the application to the Strava v3 API using OAuth2
This file requires a Strava client ID and client secret to be stored in Credentials.txt
"""

import requests
from requests import Request
import webbrowser

FILE_CREDENTIALS = 'Credentials.txt'

# Dictionary for the Strava client credentials
strava_credentials = {'client_id': '', 'client_secret': ''}

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
                strava_credentials['client_id'] = client_id         # Update the client ID in the dictionary

            if line.startswith('STRAVA_CLIENT_SECRET ='):           # Locate the client secret
                client_secret = line.split('=')[1]                  # Split the line and select the right half (2nd element)
                client_secret = client_secret.strip()               # Strip any whitespace from the client secret
                strava_credentials['client_secret'] = client_secret # Update the client secret in the dictionary

def authenticate():
    """
    Authenticates the application to the Strava v3 API using OAuth2
    """
    
    # Read the Strava credentials from the text file
    read_strava_credentials()