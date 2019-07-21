"""analysis.py

Felix van Oost 2019

Analyses and creates plots from Strava activity data.
"""

import pandas

def display_summary_statistics(activities_data_frame):
    """
    Displays the following basic statistics for each activity type:
    - Total and average distance
    - Total and average moving time
    - Total and average elevation gain
    - Average speed
    """

    # Create a data frame of summary statistics by activity type
    aggregation = {
                   'type': {'Number of activities': 'count'},
                   'distance': {'Total distance (km)': 'sum', 'Average distance (km)': 'mean'},
                   'moving_time': {'Total moving time (mins)': 'sum', 'Average moving time (mins)': 'mean'},
                   'total_elevation_gain': {'Total elevation gain (m)': 'sum', 'Average elevation gain (m)': 'mean'},
                   'average_speed': {'Average speed (km/h)': 'mean'}
                  }
    summary_statistics = activities_data_frame.groupby('type').agg(aggregation)

    # Drop the top level of columns to improve readability
    summary_statistics.columns = summary_statistics.columns.droplevel(level = 0)

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