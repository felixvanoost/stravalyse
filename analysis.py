"""analysis.py

Processes and analyses Strava athlete and activity data.

Functions:
create_activity_dataframe()
display_summary_statistics()
display_commute_statistics()
display_commute_plots()

Felix van Oost 2019
"""

# Standard library imports
import datetime

# Third-party imports
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def _generate_commute_distance_monthly_plot(commute_data: pd.DataFrame, colours: dict):
    """
    """

    # Group the commute data by month
    data = commute_data.groupby(pd.DatetimeIndex(commute_data['start_date_local']).to_period('M')).agg({'distance': 'count'})

    ax3 = sns.barplot(x=data.index.to_timestamp(),
                      y=data['distance'],
                      color='deepskyblue')
    ax3.set(title='Commutes per month', ylabel='Count', xlabel='Month')
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax3.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax3.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax3.grid(b=True, which='major', linewidth=1.0)
    ax3.grid(b=True, which='minor', linewidth=0.5)
    print(data)
    plt.show()


def _generate_commute_distance_plot(commute_data: pd.DataFrame, ax: mpl.axes.Axes, colours: dict):
    """
    """

    # Group the commute data by year
    data = commute_data.groupby(pd.DatetimeIndex(commute_data['start_date_local']).to_period('Y')).agg({'distance': ['sum', 'mean']})

    # Generate and format the plot
    sns.lineplot(x=data.index.year,
                 y=data['distance', 'sum'],
                 color=colours['commute_distance_sum'],
                 marker='o',
                 ax=ax)
    ax.set(title='Commute distance', xlabel='Year')
    ax.set_ylabel('Total distance (km)', color=colours['commute_distance_sum'])
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)

    ax_mean = plt.twinx()
    sns.lineplot(x=data.index.year,
                 y=data['distance', 'mean'],
                 color=colours['commute_distance_mean'],
                 marker='o',
                 ax=ax_mean)
    ax_mean.set_ylabel('Average distance (km)', color=colours['commute_distance_mean'])


def _generate_commute_days_plot(commute_data: pd.DataFrame, ax: mpl.axes.Axes, colours: dict):
    """
    """
    
    # Group the commute data by day
    data = commute_data.groupby(pd.DatetimeIndex(commute_data['start_date_local']).to_period('D')).agg({'distance': 'mean'})

    # Generate and format the plot
    sns.lineplot(x=data.index.year.value_counts().index,
                 y=data.index.year.value_counts(),
                 color=colours['commute_days'],
                 marker='o',
                 ax=ax)
    ax.set(title='Commute days', ylabel='Days', xlabel='Year')
    ax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
    ax.grid(b=True, which='major', linewidth=1.0)
    ax.yaxis.grid(b=True, which='minor', linewidth=0.5)


def _generate_commute_statistics(x: pd.Series) -> pd.Series:
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

    series = pd.Series(rows, index=['Number of commutes',
                                        'Total commute distance (km)',
                                        'Average commute distance (km)',
                                        'Total commute moving time (hours)',
                                        'Average commute moving time (mins)'])

    return series


def _generate_summary_statistics(x: pd.Series) -> pd.Series:
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

    series = pd.Series(rows, index=['Number of activities',
                                    'Total distance (km)',
                                    'Average distance (km)',
                                    'Total moving time (hours)',
                                    'Average moving time (mins)',
                                    'Total elevation gain (km)',
                                    'Average elevation gain (m)',
                                    'Average speed (km/h)'])

    return series


def display_commute_plots(activity_dataframe: pd.DataFrame):
    """
    Generate and display the following plots using data from activities
    marked as commutes:

    - Number of commuting days per year
    - Total and average commute distance per year
    - Number of commutes per month
    """

    # Get only commute data
    commute_data = activity_dataframe[activity_dataframe['commute'] == True][['distance', 'start_date_local']]

    # Convert the activity distances from m to km
    commute_data.loc[:, 'distance'] = commute_data.loc[:, 'distance'] / 1000

    # Create a dictionary of colours for each plot
    colours = {'commute_days': 'deepskyblue',
               'commute_distance_sum': 'deepskyblue',
               'commute_distance_mean': 'navy'}

    # Create a new figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2)
    plt.rc('axes', axisbelow=True)

    # Generate and display the plots
    _generate_commute_days_plot(commute_data, ax1, colours)
    _generate_commute_distance_plot(commute_data, ax2, colours)
    plt.show()

    _generate_commute_distance_monthly_plot(commute_data, colours)


def display_commute_statistics(activity_dataframe: pd.DataFrame):
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


def display_summary_statistics(activity_dataframe: pd.DataFrame):
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


def create_activity_dataframe(activity_data: list) -> pd.DataFrame:
    """
    Create and return a pandas DataFrame from the activity data list and
    format the dates / times to simplify visual interpretation.

    Arguments:
    activity_data - A list of detailed activity data

    Return:
    A pandas DataFrame of formatted detailed activity data
    """

    # Configure pandas to display data to 2 decimal places
    pd.set_option('precision', 2)

    # Create a pandas data frame from the Strava activities list
    activity_dataframe = pd.DataFrame.from_records(activity_data)

    # Format the activity start dates and moving / elapsed times
    activity_dataframe.loc[:, 'start_date_local_formatted'] = (activity_dataframe['start_date_local']
        .apply(lambda x: x.strftime('%e %B %Y, %H:%M:%S').strip()))
    activity_dataframe.loc[:, 'moving_time_formatted'] = (activity_dataframe['moving_time']
        .apply(lambda x: str(datetime.timedelta(seconds=x))))
    activity_dataframe.loc[:, 'elapsed_time_formatted'] = (activity_dataframe['elapsed_time']
        .apply(lambda x: str(datetime.timedelta(seconds=x))))

    return activity_dataframe