"""StravaHeatmap.py

Felix van Oost 2019

This tool generates a heatmap of Strava activities using the HERE XYZ mapping service.
"""
from datetime import datetime
import os
import strava_auth
import sys

# Add the folder containing the Strava Swagger API to the system path
sys.path.append(os.path.abspath('API'))

import swagger_client
from swagger_client.rest import ApiException

def get_last_activity_start_time(activities_list):
    """
    Gets and returns the start time of the last activity in the list.
    Returns 0 if the list is empty.
    """
    last_activity_time = 0

    if activities_list:
        # Get the start time of the last activity in the list
        last_activity_time = activities_list[0]['start_date']
    
        # Convert the ISO 8601-formatted start time into an epoch
        last_activity_time = datetime.fromisoformat(str(last_activity_time)).timestamp()
    
    return last_activity_time

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
        print('Strava: Getting activities - page {}'.format(i))
        activities = api_instance.get_logged_in_athlete_activities(after = get_last_activity_start_time(activities_list), page = i, per_page = 50)
        
        if activities:
            results.append(activities)
            i += 1
        else:
            break

    # Flatten the list of lists
    new_activities_list = [item for sublist in results for item in sublist]

    # Convert each activity object in the list into a dictionary entry
    new_activities_list = [a.to_dict() for a in new_activities_list]
    
    # Add the new activities to the activities list
    activities_list += new_activities_list

# Main module
if __name__ == "__main__":

    # Get an OAuth2 access token for the Strava v3 API
    access_token = strava_auth.get_access_token()
    
    activities = []
    update_strava_activities_list(activities, access_token)