""" run.py

Main script for the Strava Analysis Tool.

Felix van Oost 2019
"""

# Standard library imports
import argparse
import sys

# Local imports
import analysis
import geo
import strava_data


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
    args = parser.parse_args()

    # Get a list of detailed activity data for all Strava activities
    activity_data = strava_data.get_activity_data(args.refresh_data)

    # Create a pandas DataFrame from the activity data
    activity_dataframe = analysis.create_activity_dataframe(activity_data)

    # Display summary and commute statistics
    analysis.display_summary_statistics(activity_dataframe)
    analysis.display_commute_statistics(activity_dataframe)

    if args.export_geo_data:
        # Export the geospatial data from all activities in GeoJSON
        # format
        geo.export_geo_data_file(activity_dataframe)

if __name__ == "__main__":
    main()