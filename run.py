""" run.py

Main script for the Strava Analysis Tool.

Felix van Oost 2019
"""

# Standard library imports
import getopt
import sys

# Local imports
import analysis
import geo
import strava_data


def main():
    """
    Main method for the Strava Analysis Tool.

    Options:
    -r, --refresh_data - Select whether to use and update the locally
                         stored activity data or get and store a fresh
                         copy.
    """
    
    print('Strava Analysis Tool')
    print('Felix van Oost 2019')
    print()

    # Parse the command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'r', ['refresh_data'])
    except getopt.GetoptError as error:
        # Print error information and exit
        print('Error: ' + str(error))
        sys.exit(2)

    refresh_data = False

    for opt, arg in opts:
        if opt in ('-r', '--refresh_data'):
            refresh_data = True

    # Get a list of detailed activity data for all Strava activities
    activity_data = strava_data.get_activity_data(refresh_data)

    # Create a pandas DataFrame from the activity data
    activity_dataframe = analysis.create_activity_dataframe(activity_data)

    # Display summary and commute statistics
    analysis.display_summary_statistics(activity_dataframe)
    analysis.display_commute_statistics(activity_dataframe)

    # Export a GeoJSON file of geospatial data from all activities
    geo.export_geo_data_file(activity_dataframe)

if __name__ == "__main__":
    main()