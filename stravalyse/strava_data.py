"""strava_data.py

Gets and stores Strava athlete and activity data using the Strava API.

Felix van Oost 2019-2024
"""

# Standard library
from pathlib import Path
from datetime import datetime

# Third-party
import pandas as pd
from stravalib import Client

# Local
import stravalyse.geo as geo


def _parse_description_tag(activity_df: pd.DataFrame, tag_str: str, column_name: str, activity_types: list[str]) -> pd.DataFrame:
    """
    Parse the string that follows the given tag (key) in activity descriptions and store it as a new
    column in the given DataFrame.

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.
    tag_str - The tag (key) to search for in the activity descriptions.
    column_name - The name of the column in the DataFrame that will contain the parsed data.
    activity_types - The types of activities that contain the given tag.

    Return:
    The activity_df with the new column added.
    """

    # Get a Series of descriptions for the applicable activity types
    activity_desc = activity_df.loc[activity_df['sport_type'].isin(
        activity_types)]['description']

    # Parse the tag from the activity descriptions and store it as a new column in the DataFrame
    activity_df[column_name] = activity_desc.apply(
        lambda desc: desc.partition(tag_str)[2].splitlines()[0] if isinstance(desc, str) and tag_str in desc else None)

    return activity_df


def _get_activity_start_addr(activity) -> pd.DataFrame:
    """
    Get the activity start address.

    Arguments:
    activity - The activity to get the start address for.
    """

    if activity['start_address'] is None and activity['start_latlng'] is not None:
        print(f"Getting start address for {activity['name']}")
        address = geo.get_address(activity['start_latlng'])
    else:
        address = activity['start_address']

    return address


def _get_activity_end_addr(activity) -> pd.DataFrame:
    """
    Get the activity end address.

    Arguments:
    activity - The activity to get the end address for.
    """

    if activity['end_address'] is None and activity['end_latlng'] is not None:
        print(f"Getting end address for {activity['name']}")
        address = geo.get_address(activity['end_latlng'])
    else:
        address = activity['end_address']

    return address


def _read_activity_data_from_file(file_path: Path) -> pd.DataFrame:
    """
    Read the activity data from a file and return it as a pandas DataFrame.

    Arguments:
    file_path - The path of the file to read the activity data from.

    Return:
    A pandas DataFrame containing the activity data.
    An empty DataFrame if the file cannot be read from successfully.
    """

    activity_df = pd.DataFrame()

    try:
        activity_df = pd.read_json(file_path, lines=True, orient='records',
                                   convert_dates=['start_date', 'start_date_local'])

        print(f"Read {len(activity_df)} activities from '{file_path}'")
    except (ValueError, TypeError, AssertionError):
        print(f"Could not read activity data from '{file_path}'")

    return activity_df


def _write_activity_data_to_file(file_path: Path, activity_df: pd.DataFrame) -> None:
    """
    Write the activity data to a file in JSON format.

    Arguments:
    file_path - The path of the file to write the activity data to.
    activity_df - A pandas DataFrame containing the activity data.
    """

    print(f"Writing activity data to '{file_path}'")

    # Create the output directory if it doesn't already exist
    file_dir = Path(Path.cwd() / file_path).parent
    file_dir.mkdir(parents=True, exist_ok=True)

    # Write the activity DataFrame to the file
    activity_df.to_json(file_path, lines=True,
                        orient='records', date_format='iso')


def _get_last_activity_start_time(activity_df: pd.DataFrame) -> datetime:
    """
    Get and return the start time of the last activity in the given pandas DataFrame.

    Arguments:
    activity_df - A pandas DataFrame containing the activity data.

    Return:
    The start time of the last activity in the DataFrame as a datetime object.
    """

    if activity_df.empty:
        last_activity_time = "1970-01-01"
    else:
        # Get the start time of the last activity in the DataFrame
        last_activity_time = activity_df.iloc[-1]['start_date']

    return last_activity_time


def _update_activity_data(client: Client, file_path: Path, reverse_geocoding: bool,
                          activity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Update the data file and activity DataFrame with any new activities uploaded to Strava since
    the last stored activity.

    Arguments:
    access_token - An OAuth2 access token for the Strava v3 API.
    reverse_geocoding - Get and store the activity start and end addresses.
    activity_df - A pandas DataFrame containing the existing activity data.
    """

    print('Checking for new activities')

    # Get the start time of the last stored activity
    start_time = _get_last_activity_start_time(activity_df)

    new_activities = []
    try:
        activities = client.get_activities(after=start_time)

        for activity in activities:
            print(f"Getting detailed activity data for '{
                activity.name}'")

            # Get detailed activity data for each activity in the page and store it as a dictionary
            detailed_data = client.get_activity(activity.id).model_dump()

            if reverse_geocoding:
                # Get the activity start and end addresses. This is done using a reverse geocoder
                # with low API rate limits, so fetch the addresses per-activity before conversion
                # into a DataFrame in the otherwise wasted time spent waiting between the Strava API
                # 15-minute rate limits. This reduces the combined fetch time for activities +
                # addresses for larger datasets that are frequently rate-limited.
                detailed_data['start_address'] = geo.get_address(
                    detailed_data['start_latlng'])
                detailed_data['end_address'] = geo.get_address(
                    detailed_data['end_latlng'])

            new_activities.append(detailed_data)

    finally:
        print(f'Fetched {len(new_activities)} new activities')

        if new_activities:
            # Create a DataFrame with the new activities and parse the activity start dates into
            # datetime objects
            new_activities_df = pd.DataFrame(new_activities)
            new_activities_df['start_date'] = pd.to_datetime(new_activities_df['start_date'],
                                                             utc=True)
            new_activities_df['start_date_local'] = pd.to_datetime(
                new_activities_df['start_date_local'], utc=True)

            # Append the new activities to the existing DataFrame
            activity_df_updated = pd.concat(
                [activity_df, new_activities_df], ignore_index=True)

            # Write the updated activity data to the Strava activities file
            _write_activity_data_to_file(file_path, activity_df_updated)
        else:
            activity_df_updated = activity_df

    return activity_df_updated


def get_activity_data(client: Client, data_file_path: Path, config_data: dict,
                      refresh: bool = False) -> pd.DataFrame:
    """
    Get and store a pandas DataFrame of detailed data for all Strava activities.

    Arguments:
    client - The stravalib client.
    data_file_path - The path of the file to store the activity data to.
    config_data - The configuration data.
    refresh - Delete the existing activity data and get a fresh copy.

    Return:
    A pandas DataFrame containing detailed activity data.
    """

    activity_df = pd.DataFrame()

    if refresh:
        print('Refreshing activity data')

        # Force the activity data to be refreshed by deleting the file
        try:
            data_file_path.unlink()
        except OSError:
            pass
    else:
        if data_file_path.is_file():
            activity_df = _read_activity_data_from_file(data_file_path)

            # Get start and end addresses for the existing activities
            if config_data['reverse_geocoding'] and config_data['update_existing_activities']:
                print('Getting start and end addresses for existing activities')
                activity_df['start_address'] = activity_df.apply(
                    _get_activity_start_addr, axis='columns')
                activity_df['end_address'] = activity_df.apply(
                    _get_activity_end_addr, axis='columns')

                _write_activity_data_to_file(data_file_path, activity_df)

    activity_df = _update_activity_data(
        client, data_file_path, config_data['reverse_geocoding'], activity_df)

    if config_data['description_tags']:
        for tag in config_data['description_tags']:
            _parse_description_tag(
                activity_df, tag['tag_name'], tag['column_name'], tag['activity_types'])

    return activity_df
