"""strava_data.py

Gets and stores Strava athlete and activity data using the Strava v3 API.

Functions:
get_activity_data()

Felix van Oost 2019
"""

# Standard library imports
from datetime import datetime
import json
import os
import sys
import time

# Third-party imports
from dateutil import parser

# Local imports
import strava_auth
sys.path.append(os.path.abspath('API'))
import swagger_client
from swagger_client.rest import ApiException

API_RATE_LIMIT_ERROR = 429

def _iso_to_datetime(obj):
    """Deserialise ISO 8601 strings into datetime objects."""

    dictionary = {}

    for (key, value) in obj:
        # Check if the object is a string and attempt to parse it into a
        # datetime object
        if isinstance(value, str):
            try:
                dictionary[key] = parser.isoparse(value)
            except ValueError:
                dictionary[key] = value
        else:
            dictionary[key] = value

    return dictionary


class _datetime_to_iso(json.JSONEncoder):
    """
    Custom JSON encoder subclass to serialise datetime objects into ISO
    8601 strings.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            # Convert the datetime object into an ISO 8601 string
            return obj.isoformat()
        else:
            # Encode the object normally
            return json.JSONEncoder.default(self, obj)


def _read_activity_data_from_file(file_path: str) -> list:
    """
    Read the JSON-encoded activity data from a file and return it as a
    list.

    Arguments:
    file_path - The path of the file to read the activity data from.

    Return:
    A list containing the activity data.
    An empty list if the file cannot be read from successfully.
    """

    print('Strava: Reading activities from {}'.format(file_path))

    activities = []
    activities_read = 0
    try:
        with open(file_path, 'r', encoding='utf8') as file:
            for line in file.readlines():
                print('Strava: Reading activity {}'.format(activities_read), end='\r')

                # Decode each line and append it to the list
                activities.append(json.loads(line, object_pairs_hook=_iso_to_datetime))
                activities_read += 1

        # Print an empty new line to prevent the activity count display
        # from being overwritten
        print(end='\n')
    except FileNotFoundError:
        print('Strava: No activity data found in {}'.format(file_path))
        pass

    return activities


def _write_activity_data_to_file(file_path: str, activities: list):
    """
    Write a list of activity data to a file in JSON format.

    Arguments:
    file_path - The path of the file to write the activity data to.
    activities - A list of activity data to write to the file.
    """

    print('Strava: Writing activity data to {}'.format(file_path))

    # Create the Data folder if it does not already exist
    if not os.path.exists('Data'):
        os.makedirs('Data')

    # Append the activities to the file in JSON format
    with open(file_path, 'a+', encoding='utf8') as file:
        for activity in activities:
            file.write(json.dumps(activity, cls=_datetime_to_iso, ensure_ascii=False))
            file.write('\n')


def _get_last_activity_start_time(activities: list) -> int:
    """
    Get and return the start time of the last activity in the given list.

    Arguments:
    activities - A list of activity data.

    Return:
    The start time of the last activity in the list as an int.
    0 if the list is empty.
    """

    last_activity_time_epoch = 0

    if activities:
        # Get the start time of the last activity in the list
        last_activity_time_iso = str(activities[len(activities) - 1]['start_date'])

        # Convert the ISO 8601-formatted start time into an epoch
        last_activity_time_epoch = int(datetime.fromisoformat(last_activity_time_iso).timestamp())

    return last_activity_time_epoch


def _update_activity_data(access_token: str, file_path: str, activities: list):
    """
    Update the file and list of detailed activity data with any new
    activities uploaded to Strava since the last stored activity.

    Arguments:
    access_token - An OAuth2 access token for the Strava v3 API.
    activities - The list of detailed activity data to be updated.
    """

    print('Strava: Checking for new activities')

    # Create an instance of the Activities API class
    api_instance = swagger_client.ActivitiesApi()
    api_instance.api_client.configuration.access_token = access_token

    # Get the start time of the last stored activity
    start_time = _get_last_activity_start_time(activities)

    # Get and store any new activities in pages of 25
    page_count = 1
    while True:
        page = api_instance.get_logged_in_athlete_activities(after=start_time,
                                                             page=page_count,
                                                             per_page=25)

        if page:
            activities_in_page = []

            for activity in page:
                print('Strava: Getting detailed activity data for {}'.format(activity.name))

                # Get detailed activity data for each activity in the
                # page
                response = api_instance.get_activity_by_id(activity.id)

                # Convert the detailed activity data into a dictionary
                # and append it to the list of activity data from the
                # current page
                activities_in_page.append(response.to_dict())

            # Write the current page of activity data to the Strava
            # activities file
            _write_activity_data_to_file(file_path, activities_in_page)

            # Append the current page of activity data to the master
            # list of activity data
            activities += activities_in_page

            page_count += 1
        else:
            print('Strava: No new activities found')
            break


def get_activity_data(tokens_file_path: str, data_file_path: str, refresh: bool) -> list:
    """
    Get and store a list of detailed data for all Strava activities.

    Arguments:
    tokens_file_path - The path of the file to store the Strava access
                       tokens to.
    data_file_path - The path of the file to store the activity data to.
    refresh - A Boolean to select whether to use and update the locally
              stored activity data or get and store a fresh copy.

    Return:
    A list of detailed activity data.
    """

    # Get an OAuth2 access token for the Strava v3 API
    access_token = strava_auth.get_access_token(tokens_file_path)

    activities = []

    if refresh:
        print('Strava: Refreshing activity data')

        # Force the activity data to be refreshed by deleting the file
        try:
            os.remove(data_file_path)
        except OSError:
            pass
    else:
        # Read the existing activity data from the file and store a
        # local copy as a list
        activities = _read_activity_data_from_file(data_file_path)

    if access_token:
        # Update the activity data
        while True:
            try:
                _update_activity_data(access_token, data_file_path, activities)
            except ApiException as e:
                if e.status == API_RATE_LIMIT_ERROR:
                    daily_limit = int(e.headers['X-RateLimit-Limit'].split(',')[1])
                    daily_usage = int(e.headers['X-RateLimit-Usage'].split(',')[1])

                    if daily_usage >= daily_limit:
                        print('Strava: API daily limit exceeded. Exiting.')
                        break 

                    print('Strava: API 15 minute limit exceeded, Retrying in 15 minutes.')
                    time.sleep(900)
                    continue
                else:
                    print(f"Strava error: {e.status}. Message: {e.reason}.")
                    break
    else:
        print('Strava: Access to the API could not be authenticated.',
              'Only existing locally-stored activities will be processed.')

    return activities
