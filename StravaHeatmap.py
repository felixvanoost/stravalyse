"""StravaHeatmap.py

Felix van Oost 2019

This tool generates a heatmap of Strava activities using the HERE XYZ mapping service.
"""

from datetime import datetime
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

def read_activities_from_file(activities_list):
    """
    Reads the list of activities from a file in JSON format.
    """
    try:
        with open(STRAVA_ACTIVITIES_FILE, 'r') as file:
            for data in file.readlines():
                activities_list.append(json.loads(data))
    except FileNotFoundError:
        pass

def write_activities_to_file(activities_list):
    """
    Writes the list of activities to a file in JSON format.
    """

    # Create the Data folder if it does not already exist
    if not os.path.exists('Data'):
        os.makedirs('Data')

    # Append the activities to the file in JSON format
    with open(STRAVA_ACTIVITIES_FILE, 'a+') as file:
        for data in activities_list:
            file.write(json.dumps(data))
            file.write('\n')

def get_last_activity_start_time(activities_list):
    """
    Gets and returns the start time of the last activity in the list.
    Returns 0 if the list is empty.
    """

    last_activity_time_epoch = 0

    if activities_list:
        # Get the start time of the last activity in the list
        last_activity_time_iso = activities_list[len(activities_list) - 1]['start_date']

        # Convert the ISO 8601-formatted start time into an epoch
        last_activity_time_iso = last_activity_time_iso.replace("Z", "+00:00")
        last_activity_time_epoch = datetime.fromisoformat(last_activity_time_iso).timestamp()
    
    return last_activity_time_epoch

def update_activities_list(activities_list, access_token):
    """
    Updates the list of activities with any new activities since the start time of the
    last stored activity. Updates both the file and local copies of the list.
    """

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

# Main module
if __name__ == "__main__":

    # Get an OAuth2 access token for the Strava v3 API
    access_token = strava_auth.get_access_token()

    # Read the list of activities from the file and create a local copy
    activities = []
    read_activities_from_file(activities)

    # Update the list of activities
    while True:
        try:
            update_activities_list(activities, access_token)
        except ApiException:
            print('Strava: API rate limit exceeded. Retrying in {} seconds.'.format(API_RETRY_INTERVAL_SECONDS))
            time.sleep(API_RETRY_INTERVAL_SECONDS)
            continue
        break
