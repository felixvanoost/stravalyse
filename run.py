""" run.py

Main script for the Strava Analysis Tool.

Felix van Oost 2019
"""

# Local imports
import analysis
import geo
import strava_data


if __name__ == "__main__":
    """
    Main method for the Strava Analysis Tool.
    """
    
    print('Strava Analysis Tool')
    print('Felix van Oost 2019')
    print()

    # Get a list of detailed activity data for all Strava activities
    activity_data = strava_data.get_activity_data()

    # Create a pandas DataFrame from the activity data
    activity_dataframe = analysis.create_activity_dataframe(activity_data)

    # Display summary and commute statistics
    analysis.display_summary_statistics(activity_dataframe)
    analysis.display_commute_statistics(activity_dataframe)

    # Export a GeoJSON file of geospatial data from all activities
    geo.export_geo_data_file(activity_dataframe)