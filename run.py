""" run.py

Felix van Oost 2019

Main script for the Strava Heatmap Tool.
"""

import strava_activities

# Main module
if __name__ == "__main__":

    # Get a list of detailed activity data for all Strava activities
    activities = strava_activities.get_activities_list()