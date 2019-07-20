"""analysis.py

Felix van Oost 2019

Analyses and creates plots from Strava activity data.
"""

import pandas

def create_activities_data_frame(activities_list):
    """
    Creates and returns a pandas data frame from the Strava activities list and
    converts the measurement units to simplify visual interpretation.
    """

    # Create a pandas data frame from the Strava activities list
    activities_data_frame = pandas.DataFrame.from_records(activities_list)
    
    # Convert the measurement units
    activities_data_frame.loc[:, 'moving_time'] = activities_data_frame.moving_time / 60        # Convert moving time from seconds to minutes
    activities_data_frame.loc[:, 'elapsed_time'] = activities_data_frame.elapsed_time / 60      # Convert elapsed time from seconds to minutes
    activities_data_frame.loc[:, 'average_speed'] = activities_data_frame.average_speed * 3.6   # Convert average speed from m/s to km/h
    activities_data_frame.loc[:, 'max_speed'] = activities_data_frame.max_speed * 3.6           # Convert maximum speed from m/s to km/h
    activities_data_frame.loc[:, 'distance'] = activities_data_frame.distance / 1000            # Convert distance from m to km

    return activities_data_frame