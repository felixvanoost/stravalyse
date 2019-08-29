""" run.py

Felix van Oost 2019

Main script for the Strava Analysis Tool.
"""

import analysis
import geo
import strava_activities

# Main module
if __name__ == "__main__":

    # Get a list of detailed activity data for all Strava activities
    activities_list = strava_activities.get_activities_list()

    # Create a pandas DataFrame from the activities list
    activities_dataframe = analysis.create_activities_data_frame(activities_list)

    # Display summary and commute statistics
    analysis.display_summary_statistics(activities_dataframe)
    analysis.display_commute_statistics(activities_dataframe)

    # Create a GeoJSON file from the geographic activity data
    geo.create_activities_map_file(activities_dataframe)