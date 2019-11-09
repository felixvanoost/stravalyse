""" run.py

Main script for the Strava Analysis Tool.

Felix van Oost 2019
"""

# Standard library imports
import argparse
import sys

# Local imports
import analysis
import here_xyz
import geo
import strava_data

# File paths
STRAVA_ACTIVITY_DATA_FILE = 'Data/StravaActivityData.json'
STRAVA_GEO_DATA_FILE = 'Data/StravaGeoData.geojson'


def main():
    """
    Main method for the Strava Analysis Tool.
    """

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-r', '--refresh_data',
                        action='store_const',
                        const=True,
                        default=False,
                        required=False,
                        help='Get and store a fresh copy of the activity data')
    parser.add_argument('-g', '--export_geo_data',
                        action='store_const',
                        const=True,
                        default=False,
                        required=False,
                        help='Export the geospatial activity data in GeoJSON format')
    parser.add_argument('-gu', '--export_upload_geo_data',
                        action='store_const',
                        const=True,
                        default=False,
                        required=False,
                        help=('Export the geospatial activity data in GeoJSON format and upload it'
                              'to the HERE XYZ mapping platform'))
    args = parser.parse_args()

    # Get a list of detailed activity data for all Strava activities
    activity_data = strava_data.get_activity_data(STRAVA_ACTIVITY_DATA_FILE, args.refresh_data)

    # Create a pandas DataFrame from the activity data
    activity_dataframe = analysis.create_activity_dataframe(activity_data)

    # Display summary and commute statistics
    analysis.display_summary_statistics(activity_dataframe)
    analysis.display_commute_statistics(activity_dataframe)

    # Display plots
    analysis.display_commute_plots(activity_dataframe)

    if args.export_geo_data or args.export_upload_geo_data:
        # Export the geospatial data from all activities in GeoJSON
        # format
        geo.export_geo_data_file(STRAVA_GEO_DATA_FILE, activity_dataframe)

        if args.export_upload_geo_data:
            # Upload the geospatial data to HERE XYZ
            here_xyz.upload_geo_data(STRAVA_GEO_DATA_FILE)

if __name__ == "__main__":
    main()