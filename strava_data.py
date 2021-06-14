"""strava_data.py

Gets and stores Strava athlete and activity data using the Strava v3 API.

Functions:
get_activity_data()

Felix van Oost 2021
"""

# Standard library
import os
import pathlib
import sys
import time

# Third-party
from dateutil import parser
import pandas

# Local
sys.path.append(os.path.abspath('API'))
import swagger_client
import strava_auth

API_RATE_LIMIT_ERROR = 429


def _read_activity_data_from_file(file_path: pathlib.Path) -> pandas.DataFrame:
    """
    Read the activity data from a file and return it as a pandas DataFrame.

    Arguments:
    file_path - The path of the file to read the activity data from.

    Return:
    A pandas DataFrame containing the activity data.
    An empty DataFrame if the file cannot be read from successfully.
    """

    activities = pandas.DataFrame()

    try:
        activities = pandas.read_json(file_path, lines=True, orient='records')

        print("[Strava]: Read {} activities from '{}'".format(len(activities), file_path))
    except (ValueError, TypeError, AssertionError):
        print("[Strava]: Could not read activity data from '{}'".format(file_path))

    return activities


def _write_activity_data_to_file(file_path: pathlib.Path, activities: pandas.DataFrame):
    """
    Write the activity data to a file in JSON format.

    Arguments:
    file_path - The path of the file to write the activity data to.
    activities - A pandas DataFrame containing the activity data to write to the file.
    """

    print("[Strava]: Writing activity data to '{}'".format(file_path))

    # Create the output directory if it doesn't already exist
    file_dir = pathlib.Path(pathlib.Path.cwd() / file_path).parent
    file_dir.mkdir(parents=True, exist_ok=True)

    # Write the activities to the file
    activities.to_json(file_path, lines=True, orient='records', date_format='iso')


def _get_last_activity_start_time(activities: pandas.DataFrame) -> int:
    """
    Get and return the start time of the last activity in the given pandas DataFrame.

    Arguments:
    activities - A pandas DataFrame containing the activity data.

    Return:
    The start time of the last activity in the DataFrame as an int.
    0 if the DataFrame is empty.
    """

    last_activity_time_epoch = 0

    if not activities.empty:
        # Get the start time of the last activity in the DataFrame
        last_activity_time_iso = parser.isoparse(activities.iloc[-1]['start_date'])

        # Convert the ISO 8601-formatted start time into an epoch
        last_activity_time_epoch = int(last_activity_time_iso.timestamp())

    return last_activity_time_epoch


def _update_activity_data(access_token: str, file_path: pathlib.Path,
                          activities: pandas.DataFrame) -> pandas.DataFrame:
    """
    Update the data file and activity DataFrame with any new activities uploaded to Strava since
    the last stored activity.

    Arguments:
    access_token - An OAuth2 access token for the Strava v3 API.
    activities - The pandas DataFrame of detailed activity data to be updated.
    """

    print('[Strava]: Checking for new activities')

    # Create an instance of the Activities API class
    api_instance = swagger_client.ActivitiesApi()
    api_instance.api_client.configuration.access_token = access_token

    # Get the start time of the last stored activity
    start_time = _get_last_activity_start_time(activities)

    # Get and store any new activities in pages of 50
    new_activities = []
    page_count = 1
    try:
        while True:
            page = api_instance.get_logged_in_athlete_activities(after=start_time,
                                                                    page=page_count,
                                                                    per_page=50)

            if page:
                for activity in page:
                    print("[Strava]: Getting detailed activity data for '{}'".format(activity.name))

                    # Get detailed activity data for each activity in the page
                    detailed_data = api_instance.get_activity_by_id(activity.id)

                    # Convert the detailed activity data into a dictionary and append it to the list
                    # of activity data from the current page
                    new_activities.append(detailed_data.to_dict())

                page_count += 1
            else:
                print('[Strava]: No new activities found')
                break

            page = api_instance.get_logged_in_athlete_activities(after=start_time,
                                                             page=page_count,
                                                             per_page=25)

    finally:
        if new_activities:
            # Append the new activities to the existing DataFrame
            activities_updated = activities.append(pandas.DataFrame(new_activities),
                                                   ignore_index=True)

            # Write the updated activity data to the Strava activities file
            _write_activity_data_to_file(file_path, activities_updated)
        else:
            activities_updated = activities

    return activities_updated


def get_activity_data(tokens_file_path: pathlib.Path, data_file_path: pathlib.Path,
                      refresh: bool) -> pandas.DataFrame:
    """
    Get and store a pandas DataFrame of detailed data for all Strava activities.

    Arguments:
    tokens_file_path - The path of the file to store the Strava access tokens to.
    data_file_path - The path of the file to store the activity data to.
    refresh - A Boolean to select whether to use and update the locally stored activity data or get
              and store a fresh copy.

    Return:
    A pandas DataFrame of detailed activity data.
    """

    # Get an OAuth2 access token for the Strava v3 API
    access_token = strava_auth.get_access_token(tokens_file_path)

    activities = pandas.DataFrame()

    if refresh:
        print('[Strava]: Refreshing activity data')

        # Force the activity data to be refreshed by deleting the file
        try:
            data_file_path.unlink()
        except OSError:
            pass
    else:
        if data_file_path.is_file():
            # Read the existing activity data from the file
            activities = _read_activity_data_from_file(data_file_path)

    if access_token:
        # Update the activity data
        while True:
            try:
                activities = _update_activity_data(access_token, data_file_path, activities)
            except swagger_client.rest.ApiException as error:
                if error.status == API_RATE_LIMIT_ERROR:
                    daily_limit = int(error.headers['X-RateLimit-Limit'].split(',')[1])
                    daily_usage = int(error.headers['X-RateLimit-Usage'].split(',')[1])

                    if daily_usage >= daily_limit:
                        print('[Strava]: API daily rate limit exceeded. Exiting.')
                        break

                    print('[Strava]: API 15 minute rate limit exceeded. Retrying in 15 minutes.')
                    time.sleep(900)
                else:
                    print(f'[Error]: {error.status}. Message: {error.reason}.')
                    break
            break
    else:
        print('[Strava]: Access to the API could not be authenticated.',
              'Only existing locally-stored activities will be processed.')

    return activities
