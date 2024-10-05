"""strava_data.py

Gets and stores Strava athlete and activity data using the Strava API.

Felix van Oost 2024
"""

# Standard library
import pathlib
from datetime import datetime

# Third-party
import pandas as pd
from stravalib import Client


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
        lambda desc: desc.partition(tag_str)[2].splitlines()[0] if tag_str in desc else None)

    return activity_df


def _read_activity_data_from_file(file_path: pathlib.Path) -> pd.DataFrame:
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
        print(f"[Strava]: Could not read activity data from '{file_path}'")

    return activity_df


def _write_activity_data_to_file(file_path: pathlib.Path, activity_df: pd.DataFrame) -> None:
    """
    Write the activity data to a file in JSON format.

    Arguments:
    file_path - The path of the file to write the activity data to.
    activity_df - A pandas DataFrame containing the activity data.
    """

    print(f"Writing activity data to '{file_path}'")

    # Create the output directory if it doesn't already exist
    file_dir = pathlib.Path(pathlib.Path.cwd() / file_path).parent
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


def _update_activity_data(client: Client, file_path: pathlib.Path,
                          activity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Update the data file and activity DataFrame with any new activities uploaded to Strava since
    the last stored activity.

    Arguments:
    access_token - An OAuth2 access token for the Strava v3 API.
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
            new_activities.append(
                client.get_activity(activity.id).model_dump())
    finally:
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


def get_activity_data(client: Client, data_file_path: pathlib.Path, description_tags: list[dict],
                      refresh: bool) -> pd.DataFrame:
    """
    Get and store a pandas DataFrame of detailed data for all Strava activities.

    Arguments:
    client - The stravalib client.
    data_file_path - The path of the file to store the activity data to.
    description_tags - List of description tags to parse.
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
            # Read the existing activity data from the file
            activity_df = _read_activity_data_from_file(data_file_path)

    activity_df = _update_activity_data(client, data_file_path, activity_df)

    if description_tags:
        for tag in description_tags:
            _parse_description_tag(
                activity_df, tag['tag_name'], tag['column_name'], tag['activity_types'])

    return activity_df
