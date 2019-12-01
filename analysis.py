"""analysis.py

Processes and analyses Strava athlete and activity data.

Functions:
create_activity_dataframe()
display_summary_statistics()
display_commute_statistics()

Felix van Oost 2019
"""

# Standard library imports
import datetime

# Third-party imports
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas
import seaborn as sns


def display_commute_plots(activity_dataframe: pandas.DataFrame):
    """
    Generate and display the following plots using data from activities
    marked as commutes:

    - Number of commuting days per year
    - Total and average commuting distance per year
    - Number of commutes per month
    """

    # Get only commute data
    data = activity_dataframe[activity_dataframe['commute'] == True][['distance', 'start_date_local']]

    # Convert the activity distances from m to km
    data.loc[:, 'distance'] = data.loc[:, 'distance'] / 1000

    # Aggregate all the activities from one day into a single entry
    data1 = data.groupby(pandas.DatetimeIndex(data['start_date_local']).to_period('D')).agg({'distance': ['sum', 'mean']}).reset_index()

    # Create a new figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2)

    # Plot the number of commuting days per year
    sns.lineplot(x=pandas.PeriodIndex(data1['start_date_local']).year.value_counts().index,
                 y=pandas.PeriodIndex(data1['start_date_local']).year.value_counts(),
                 color='deepskyblue',
                 markers=True,
                 ax=ax1)
    ax1.set(title='Commuting days', ylabel='Days', xlabel='Year')
    ax1.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax1.grid(b=True, which='major', linewidth=1.0)
    ax1.grid(b=True, which='minor', linewidth=0.5)

    # Plot the average commuting distance per year
    sns.lineplot(x=pandas.PeriodIndex(data1['start_date_local']).year,
                 y=data1['distance', 'mean'],
                 color='deepskyblue',
                 markers=True,
                 data=data,
                 ax=ax2)
    ax2.set(title='Average commuting distance', ylabel='Distance (km)', xlabel='Year')
    ax2.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax2.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax2.grid(b=True, which='major', linewidth=1.0)
    ax2.grid(b=True, which='minor', linewidth=0.5)

    # Plot the average number of communtes per month

    plt.show()


def _generate_commute_statistics(x: pandas.Series) -> pandas.Series:
    """
    Generate basic commute statistics from a given pandas Series.

    Arguments:
    x - The Series to generate basic commute statistics from. 

    Return:
    A Series containing the following commute statistics:
    - Number of commutes
    - Total and average commute distance
    - Total and average commute time
    """

    rows = {'Number of commutes': x['type'].count(),
            'Total commute distance (km)': x['distance'].sum() / 1000,
            'Average commute distance (km)': x['distance'].mean() / 1000,
            'Total commute moving time (hours)': x['moving_time'].sum() / 3600,
            'Average commute moving time (mins)': x['moving_time'].mean() / 60}

    series = pandas.Series(rows, index=['Number of commutes',
                                        'Total commute distance (km)',
                                        'Average commute distance (km)',
                                        'Total commute moving time (hours)',
                                        'Average commute moving time (mins)'])

    return series


def _generate_summary_statistics(x: pandas.Series) -> pandas.Series:
    """
    Generate basic statistics from a given pandas Series.

    Arguments:
    x - The Series to generate basic commute statistics from. 

    Return:
    A Series containing the following statistics:
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

    series = pandas.Series(rows, index=['Number of activities',
                                        'Total distance (km)',
                                        'Average distance (km)',
                                        'Total moving time (hours)',
                                        'Average moving time (mins)',
                                        'Total elevation gain (km)',
                                        'Average elevation gain (m)',
                                        'Average speed (km/h)'])

    return series


def display_commute_statistics(activity_dataframe: pandas.DataFrame):
    """
    Display basic commute statistics for each activity type.

    Arguments:
    activity_dataframe - A pandas DataFrame containing the activity data.
    """

    commute_dataframe = activity_dataframe[activity_dataframe['commute'] == True]

    if not commute_dataframe.empty:
        commute_statistics = commute_dataframe.groupby('type').apply(_generate_commute_statistics)

        print('Commute statistics:')
        print()
        print(commute_statistics.T)
        print()
    else:
        print('Analysis: No commutes found')


def display_summary_statistics(activity_dataframe: pandas.DataFrame):
    """
    Display basic statistics for each activity type.

    Arguments:
    activity_dataframe - A pandas DataFrame containing the activity data.
    """

    if not activity_dataframe.empty:
        summary_statistics = activity_dataframe.groupby('type').apply(_generate_summary_statistics)

        print()
        print('Summary statistics:')
        print()
        print(summary_statistics.T)
        print()
    else:
        print('Analysis: No activities found')


def create_activity_dataframe(activity_data: list) -> pandas.DataFrame:
    """
    Create and return a pandas DataFrame from the activity data list and
    format the dates / times to simplify visual interpretation.

    Arguments:
    activity_data - A list of detailed activity data

    Return:
    A pandas DataFrame of formatted detailed activity data
    """

    # Configure pandas to display data to 2 decimal places
    pandas.set_option('precision', 2)

    # Create a pandas data frame from the Strava activities list
    activity_dataframe = pandas.DataFrame.from_records(activity_data)

    # Format the activity start dates and moving / elapsed times
    activity_dataframe.loc[:, 'start_date_local_formatted'] = (activity_dataframe['start_date_local']
        .apply(lambda x: x.strftime('%e %B %Y, %H:%M:%S').strip()))
    activity_dataframe.loc[:, 'moving_time_formatted'] = (activity_dataframe['moving_time']
        .apply(lambda x: str(datetime.timedelta(seconds=x))))
    activity_dataframe.loc[:, 'elapsed_time_formatted'] = (activity_dataframe['elapsed_time']
        .apply(lambda x: str(datetime.timedelta(seconds=x))))

    return activity_dataframe