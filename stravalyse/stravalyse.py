""" stravalyse.py

Main module for Stravalyse.

Felix van Oost 2024
"""

# Standard library
import argparse
import datetime
from pathlib import Path
import sys

# Third-party
import pandas as pd
from stravalib import Client
from toml import load

# Local
import stravalyse.analysis as analysis
import stravalyse.geo as geo
import stravalyse.strava_auth as strava_auth
import stravalyse.strava_data as strava_data

# Configuration file path
CONFIG_FILE_PATH = 'config.toml'


def main():
    """
    Main method for Stravalyse.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-a', '--activity_count_plot',
                        action='store_true',
                        required=False,
                        help='Generate and display a plot of activity counts over time')
    parser.add_argument('-c', '--commute_plots',
                        action='store_true',
                        required=False,
                        help='Generate and display plots of the commute data')
    parser.add_argument('-d', '--mean_distance_plot',
                        action='store_true',
                        required=False,
                        help='Generate and display a plot of the mean activity distance over time')
    parser.add_argument('-g', '--export_geo_data',
                        action='store_true',
                        required=False,
                        help='Export the geospatial activity data in GeoJSON format')
    parser.add_argument('-gu', '--export_upload_geo_data',
                        action='store_true',
                        required=False,
                        help=('Export the geospatial activity data in GeoJSON format and upload it'
                              ' to the HERE XYZ mapping platform'))
    parser.add_argument('-l', '--start_locations_plot',
                        action='store_true',
                        required=False,
                        help=('Generate and display a plot of the number of activities started'
                              ' in each country'))
    parser.add_argument('-m', '--moving_time_heatmap',
                        action='store_true',
                        required=False,
                        help='Generate and display a heatmap of moving time for each activity type')
    parser.add_argument('-r', '--refresh_data',
                        action='store_true',
                        required=False,
                        help='Get and store a fresh copy of the activity data')
    parser.add_argument('--date_range_start',
                        action='store',
                        default=None,
                        required=False,
                        type=datetime.datetime.fromisoformat,
                        help='Specify the start of a date range in ISO format')
    parser.add_argument('--date_range_end',
                        action='store',
                        default=None,
                        required=False,
                        type=datetime.datetime.fromisoformat,
                        help='Specify the end of a date range in ISO format')
    args = parser.parse_args()

    # Load the TOML configuration
    config = load(CONFIG_FILE_PATH)

    # Configure pandas to display float values to 2 decimal places
    pd.options.display.float_format = "{:,.2f}".format

    # Authenticate with the Strava API
    client: Client = strava_auth.authenticate(Path(
        config['paths']['strava_tokens_file']))

    # Create a pandas DataFrame of detailed Strava activity data
    activity_df: pd.DataFrame = strava_data.get_activity_data(client,
                                                              Path(
                                                                  config['paths']['activity_data_file']),
                                                              config['data'],
                                                              args.refresh_data)

    if args.date_range_start is not None or args.date_range_end is not None:
        date_mask = [True] * len(activity_df)

        if args.date_range_start is not None:
            # Add timezone information to the start date
            args.date_range_start = args.date_range_start.replace(
                tzinfo=datetime.timezone.utc)

            # Add the start date to the date mask
            date_mask = (date_mask &
                         (activity_df['start_date_local'] >= args.date_range_start))

        if args.date_range_end is not None:
            # Add timezone information to the end date
            args.date_range_end = args.date_range_end.replace(
                tzinfo=datetime.timezone.utc)

            if args.date_range_start is not None and args.date_range_end < args.date_range_start:
                sys.exit('[ERROR]: End date must be later than start date')
            else:
                # Add the end date to the date mask
                date_mask = (date_mask &
                             (activity_df['start_date_local'] <= args.date_range_end))

        # Apply the date mask to the activity DataFrame
        activity_df = activity_df[date_mask]

    # Display summary and commute statistics
    analysis.display_summary_statistics(activity_df)
    analysis.display_commute_statistics(activity_df)

    if args.export_geo_data or args.export_upload_geo_data:
        # Export the geospatial data from all activities in GeoJSON format
        geo.export_geo_data_file(
            config['paths']['geo_data_file'], activity_df)

    if args.activity_count_plot:
        # Generate and display a plot of activity counts over time
        analysis.display_activity_count_plot(activity_df,
                                             config['analysis']['plot_colour_palette'])

    if args.commute_plots:
        # Generate and display plots of the commute data
        analysis.display_commute_plots(activity_df,
                                       config['analysis']['plot_colour_palette'])

    if args.mean_distance_plot:
        # Generate and display a plot of the mean activity distance over time
        analysis.display_mean_distance_plot(activity_df,
                                            config['analysis']['plot_colour_palette'])

    if args.start_locations_plot:
        if config['data']['enable_reverse_geocoding']:
            # Generate and display a plot of the number of activities started in each country
            analysis.display_start_country_plot(activity_df,
                                                config['analysis']['plot_colour_palette'])
        else:
            print("Reverse geocoding must be enabled to generate this plot.",
                  f"Set 'enable_reverse_geocoding' in {
                      CONFIG_FILE_PATH} to 'true',",
                  "then refresh the activity data using the argument '-r'.")

    if args.moving_time_heatmap:
        # Generate and display a heatmap of moving time for each activity type
        analysis.display_moving_time_heatmap(activity_df,
                                             config['analysis']['heatmap_colour_palette'],
                                             config['analysis']['heatmap_column_wrap'])


if __name__ == "__main__":
    main()
