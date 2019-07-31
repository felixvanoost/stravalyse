"""analysis.py

Felix van Oost 2019

Analyses and creates plots from Strava activity data.
"""

import pandas

def generate_summary_statistics(x):
    """
    Generates the following basic statistics from the activities data frame:
    - Total and average distance
    - Total and average moving time
    - Total and average elevation gain
    - Average speed
    """

    rows = {
            'Number of activities': x['type'].count(),
            'Total distance (km)':  x['distance'].sum(),
            'Average distance (km)':  x['distance'].mean(),
            'Total moving time (hours)':  (x['moving_time'].sum() / 60),
            'Average moving time (mins)':  x['moving_time'].mean(),
            'Total elevation gain (km)':  (x['total_elevation_gain'].sum() / 1000),
            'Average elevation gain (m)':  x['total_elevation_gain'].mean(),
            'Average speed (km/h)':  x['average_speed'].mean()
           }

    series = pandas.Series(rows, index = ['Number of activities', 'Total distance (km)', 'Average distance (km)', 'Total moving time (hours)',
                                          'Average moving time (mins)', 'Total elevation gain (km)', 'Average elevation gain (m)', 'Average speed (km/h)'])

    return series

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
    
    # Convert the measurement units
    activities_data_frame.loc[:, 'distance'] = activities_data_frame['distance'] / 1000             # Convert distance from m to km
    activities_data_frame.loc[:, 'moving_time'] = activities_data_frame['moving_time'] / 60         # Convert moving time from seconds to minutes
    activities_data_frame.loc[:, 'elapsed_time'] = activities_data_frame['elapsed_time'] / 60       # Convert elapsed time from seconds to minutes
    activities_data_frame.loc[:, 'average_speed'] = activities_data_frame['average_speed'] * 3.6    # Convert average speed from m/s to km/h
    activities_data_frame.loc[:, 'max_speed'] = activities_data_frame['max_speed'] * 3.6            # Convert maximum speed from m/s to km/h

    return activities_data_frame