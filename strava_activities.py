"""strava_activities.py

Felix van Oost 2019

Obtains and stores detailed activity data for all Strava activities. 
"""

from datetime import datetime
from dateutil import parser
import json
import os
import strava_auth
import sys
import time

# Add the folder containing the Strava Swagger API to the system path
sys.path.append(os.path.abspath('API'))

import swagger_client
from swagger_client.rest import ApiException

# File paths
STRAVA_ACTIVITIES_FILE = 'Data/StravaActivities.json'

# Constants
API_RETRY_INTERVAL_SECONDS = (2 * 60)

def iso_to_datetime(obj):
    """
    JSON decoder hook to deserialise ISO 8601 strings into datetime objects.
    """

    dictionary = {}

    for (key, value) in obj:
        # Check if the object is a string and attempt to parse it into a datetime object
        if isinstance(value, str):
            try:
                dictionary[key] = parser.parse(value)
            except ValueError:
                dictionary[key] = value
        else:
            dictionary[key] = value

    return dictionary

class datetime_to_iso(json.JSONEncoder):
    """
    Custom JSON encoder subclass to serialise datetime objects into ISO 8601 strings.
    """
    
    def default(self, obj):
        if isinstance(obj, datetime):
            # Convert the datetime object into an ISO 8601 string
            return obj.isoformat()
        else:
            # Encode the object normally
            return json.JSONEncoder.default(self, obj)

def read_activities_from_file(activities_list):
    """
    Reads the list of activities from a file in JSON format.
    """

    print('Strava: Reading activities from {}'.format(STRAVA_ACTIVITIES_FILE))

    activities_read = 0
    try:
        with open(STRAVA_ACTIVITIES_FILE, 'r') as file:
            for data in file.readlines():
                print('Strava: Reading activity {}'.format(activities_read), end = "\r")

                # Decode each JSON formatted line from the file and append it to the activities list
                activities_list.append(json.loads(data, object_pairs_hook = iso_to_datetime))
                activities_read += 1
    except FileNotFoundError:
        pass

    # Empty new line to prevent the activity count display from being overwritten
    print(end = "\n")

def write_activities_to_file(activities):
    """
    Writes an arbitrary list of activities to a file in JSON format.
    """

    print('Strava: Writing activities to {}'.format(STRAVA_ACTIVITIES_FILE))

    # Create the Data folder if it does not already exist
    if not os.path.exists('Data'):
        os.makedirs('Data')

    # Append the activities to the file in JSON format
    with open(STRAVA_ACTIVITIES_FILE, 'a+') as file:
        for data in activities:
            file.write(json.dumps(data, cls = datetime_to_iso))
            file.write('\n')

def get_last_activity_start_time(activities_list):
    """
    Gets and returns the start time of the last activity in the list.
    Returns 0 if the list is empty.
    """

    last_activity_time_epoch = 0

    if activities_list:
        # Get the start time of the last activity in the list
        last_activity_time_iso = str(activities_list[len(activities_list) - 1]['start_date'])

        # Convert the ISO 8601-formatted start time into an epoch
        last_activity_time_epoch = datetime.fromisoformat(last_activity_time_iso).timestamp()
    
    return last_activity_time_epoch

def update_activities_list(activities_list, access_token):
    """
    Updates the list of activities with any new activities since the start time of the
    last stored activity. Updates both the file and local copies of the list.
    """

    print('Strava: Checking for new activities')

    # Create an instance of the Activities API class
    api_instance = swagger_client.ActivitiesApi()
    api_instance.api_client.configuration.access_token = access_token

    # Get the start time of the last activity in the list of activities
    start_time = get_last_activity_start_time(activities_list)

    # Get and store any new activities in pages of 50
    page_count = 1
    while True:
        page = api_instance.get_logged_in_athlete_activities(after = start_time, page = page_count, per_page = 50)

        if page:
            activities_in_page = []

            for activity in page:
                print('Strava: Getting detailed activity data for {}'.format(activity.name))

                # Get the detailed activity data for each activity in the page
                response = api_instance.get_activity_by_id(activity.id)

                # Convert the detailed activity data into a dictionary entry and append it to the list of activities in the current page
                activities_in_page.append(response.to_dict())

            # Append the current page of activities to the Strava activities file
            write_activities_to_file(activities_in_page)

            # Append the current page of activities to the local copy of the list
            activities_list += activities_in_page

            page_count += 1
        else:
            print('Strava: No new activities found')
            break

def get_activities_list():
    """
    Gets and stores a list of detailed activity data for all Strava activities.
    Returns a local copy of the list.
    """

    # Get an OAuth2 access token for the Strava v3 API
    access_token = strava_auth.get_access_token()

    # Read the existing list of activities from the file and create a local copy
    activities_list = []
    read_activities_from_file(activities_list)

    # Update the list of activities
    while True:
        try:
            update_activities_list(activities_list, access_token)
        except ApiException:
            print('Strava: API rate limit exceeded. Retrying in {} seconds.'.format(API_RETRY_INTERVAL_SECONDS))
            time.sleep(API_RETRY_INTERVAL_SECONDS)
            continue
        break

    return activities_list
