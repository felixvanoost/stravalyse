""" strava_analysis_tool.py

Main module for the Strava Analysis Tool.

Felix van Oost 2021
"""

# Standard library
import argparse
import datetime
import pathlib
import sys

# Third-party
import pandas
import toml

# Local
import analysis
import here_xyz
import geo
import strava_data

# Configuration file path
CONFIG_FILE_PATH = 'config.toml'


def main():
    """
    Main method for the Strava Analysis Tool.
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
    config = toml.load(CONFIG_FILE_PATH)

    # Configure pandas to display data to 2 decimal places
    pandas.set_option('precision', 2)

    # Get a list of detailed data for all Strava activities
    activity_df = strava_data.get_activity_data(pathlib.Path(config['paths']['tokens_file']),
                                                pathlib.Path(config['paths']['activity_data_file']),
                                                args.refresh_data,
                                                config['data']['enable_reverse_geocoding'])

    if args.date_range_start is not None or args.date_range_end is not None:
        date_mask = [True] * len(activity_df)

        if args.date_range_start is not None:
            # Add timezone information to the start date
            args.date_range_start = args.date_range_start.replace(tzinfo=datetime.timezone.utc)

            # Add the start date to the date mask
            date_mask = (date_mask &
                         (activity_df['start_date_local'] >= args.date_range_start))

        if args.date_range_end is not None:
            # Add timezone information to the end date
            args.date_range_end = args.date_range_end.replace(tzinfo=datetime.timezone.utc)

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
        geo.export_geo_data_file(config['paths']['geo_data_file'], activity_df)

        if args.export_upload_geo_data:
            # Upload the geospatial data to HERE XYZ
            here_xyz.upload_geo_data(config['paths']['geo_data_file'])

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

    if args.moving_time_heatmap:
        # Generate and display a heatmap of moving time for each activity type
        analysis.display_moving_time_heatmap(activity_df,
                                             config['analysis']['heatmap_colour_palette'],
                                             config['analysis']['heatmap_column_wrap'])


if __name__ == "__main__":
    main()
