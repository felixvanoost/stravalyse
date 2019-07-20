""" run.py

Felix van Oost 2019

Main script for the Strava Heatmap Tool.
"""

import analysis
import strava_activities

# Main module
if __name__ == "__main__":

    # Get a list of detailed activity data for all Strava activities
    activities_list = strava_activities.get_activities_list()

    # Create a pandas data frame from the activities list
    activities_data_frame = analysis.create_activities_data_frame(activities_list)