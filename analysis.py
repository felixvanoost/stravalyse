"""analysis.py

Felix van Oost 2019

Analyses and creates plots from Strava activity data.
"""

import datetime
import pandas

def generate_commute_statistics(x):
    """
    Generates the following basic commute statistics from the activities data frame:
    - Number of commutes
    - Total and average commute distance
    - Total and average commute time
    """

    rows = {'Number of commutes': x['type'].count(),
            'Total commute distance (km)': x['distance'].sum() / 1000,
            'Average commute distance (km)': x['distance'].mean() / 1000,
            'Total commute moving time (hours)': x['moving_time'].sum() / 3600,
            'Average commute moving time (mins)': x['moving_time'].mean() / 60}

    series = pandas.Series(rows, index=['Number of commutes', 'Total commute distance (km)', 'Average commute distance (km)',
                                        'Total commute moving time (hours)', 'Average commute moving time (mins)'])

    return series

def generate_summary_statistics(x):
    """
    Generates the following basic statistics from the activities data frame:
    - Total and average distance
    - Total and average moving time
    - Total and average elevation gain
    - Average speed
    """

    rows = {'Number of activities': x['type'].count(),
            'Total distance (km)': x['distance'].sum() / 1000,
            'Average distance (km)': x['distance'].mean() / 1000,
            'Total moving time (hours)': x['moving_time'].sum() / 3600,
            'Average moving time (mins)': x['moving_time'].mean() / 60,
            'Total elevation gain (km)': x['total_elevation_gain'].sum() / 1000,
            'Average elevation gain (m)': x['total_elevation_gain'].mean(),
            'Average speed (km/h)': x['average_speed'].mean() * 3.6}

    series = pandas.Series(rows, index=['Number of activities', 'Total distance (km)', 'Average distance (km)', 'Total moving time (hours)', 'Average moving time (mins)',
                                          'Total elevation gain (km)', 'Average elevation gain (m)', 'Average speed (km/h)'])

    return series

def display_commute_statistics(activities_data_frame):
    """
    Displays basic commute statistics for each activity type.
    """

    commute_statistics = activities_data_frame[activities_data_frame['commute'] == True].groupby('type').apply(generate_commute_statistics)

    pandas.set_option('display.max_rows', None)
    print()
    print('Commute statistics:')
    print()
    print(commute_statistics.T)

def display_summary_statistics(activities_data_frame):
    """
    Displays basic statistics for each activity type.
    """

    summary_statistics = activities_data_frame.groupby('type').apply(generate_summary_statistics)

    print()
    print('Summary statistics:')
    print()
    print(summary_statistics.T)

def create_activities_data_frame(activities_list):
    """
    Creates and returns a pandas data frame from the Strava activities list and
    converts the measurement units to simplify visual interpretation.
    """

    # Configure pandas to display data to 2 decimal places
    pandas.set_option('precision', 2)

    # Create a pandas data frame from the Strava activities list
    activities_data_frame = pandas.DataFrame.from_records(activities_list)

    # Format the activity start dates and moving / elapsed times
    activities_data_frame.loc[:, 'start_date_local_formatted'] = activities_data_frame['start_date_local'].apply(lambda x: x.strftime('%e %B %Y, %H:%M:%S').strip())
    activities_data_frame.loc[:, 'moving_time_formatted'] = activities_data_frame['moving_time'].apply(lambda x: str(datetime.timedelta(seconds=x)))
    activities_data_frame.loc[:, 'elapsed_time_formatted'] = activities_data_frame['elapsed_time'].apply(lambda x: str(datetime.timedelta(seconds=x)))

    return activities_data_frame