"""StravaHeatmap.py

Felix van Oost 2019

This tool generates a heatmap of Strava activities using the HERE XYZ mapping service.
"""

from datetime import datetime
import json
import os
import strava_auth
import sys

# Add the folder containing the Strava Swagger API to the system path
sys.path.append(os.path.abspath('API'))

import swagger_client
from swagger_client.rest import ApiException

# File paths
STRAVA_ACTIVITIES_FILE = 'Data/StravaActivities.json'

def read_activities_from_file():
    """
    Reads the activities list from a file in JSON format.
    """

    with open(STRAVA_ACTIVITIES_FILE, 'r') as file:
        for data in file.readlines():
            activities.append(json.loads(data))

def write_activities_to_file():
    """
    Writes the activities list to a file in JSON format.
    """

    # Create the Data folder if it does not already exist
    if not os.path.exists('Data'):
        os.makedirs('Data')

    # Write the activities to the file in JSON format
    with open(STRAVA_ACTIVITIES_FILE, 'w+') as file:
        for data in activities:
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

def update_strava_activities_list(activities_list, access_token):
    """
    Updates the list of Strava activities since the start time of the last stored activity.
    """

    # Create an instance of the Activities API class
    api_instance = swagger_client.ActivitiesApi()
    api_instance.api_client.configuration.access_token = access_token

    # Get the new activities in pages of 50
    results = []
    i = 1
    while True:
        activities = api_instance.get_logged_in_athlete_activities(after = get_last_activity_start_time(activities_list), page = i, per_page = 50)
        
        if activities:
            print('Strava: Getting activities - page {}'.format(i))
            results.append(activities)
            i += 1
        else:
            print('Strava: No new activities found')
            break

    # Flatten the list of lists
    new_activities_list = [item for sublist in results for item in sublist]

    # Convert each activity object in the list into a dictionary entry
    new_activities_list = [a.to_dict() for a in new_activities_list]
    
    # Add the new activities to the activities list
    activities_list += new_activities_list

# Main module
if __name__ == "__main__":

    activities = []

    # Get an OAuth2 access token for the Strava v3 API
    access_token = strava_auth.get_access_token()

    # Read the existing activities list from the file
    read_activities_from_file()

    # Update the activities list with any new activities
    update_strava_activities_list(activities, access_token)

    # Write the activities list back to the file
    write_activities_to_file()