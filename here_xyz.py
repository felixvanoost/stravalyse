"""here_xyz.py

Uploads and manages the geospatial data from Strava activities with the
HERE XYZ mapping platform.

Functions:
upload_geo_data()

Felix van Oost 2019
"""

# Standard library
import os
import sys

# Third-party
import xyzspaces


def _get_space(xyz) -> object:
    """
    Get and return an instance of the space containing the Strava activity data
    or create a new space if one does not currently exist.

    Return:
    An instance of the space containing the Strava activity data.
    """

    print('[HERE XYZ]: Locating the Strava activity data space')

    # Get a list of existing spaces
    spaces_list = xyz.spaces.list(owner='me')

    # Search for an existing space with the name 'Strava Activity Data'
    for space in spaces_list:
        if space['title'] == 'Strava Activity Data':
            space_id = space['id']

            print("[HERE XYZ]: Found space with ID '{}'".format(space_id))

            space_obj = xyz.spaces.from_id(space_id)
            break

    if not space_obj:
        print('[HERE XYZ]: No existing space found')

        # Create a new space
        space_obj = xyz.spaces.new(title='Strava Activity Data',
                                   description='Created by Strava Analysis Tool')

        print("[HERE XYZ]: Created new space with ID '{}'".format(space_obj.info['id']))

    return space_obj


def upload_geo_data(file_path: str):
    """
    Upload the geospatial data from Strava activities to the HERE XYZ mapping
    platform.

    Arguments:
    file_path - The path of the file containing the geospatial activity
                data.
    """

    try:
        xyz_token = os.environ['XYZ_TOKEN']
    except KeyError:
        sys.exit('[ERROR]: Add XYZ_TOKEN to your environment variables')

    xyz = xyzspaces.XYZ(credentials=xyz_token)

    # Get the space containing the geospatial activity data
    space = _get_space(xyz)

    print("[HERE XYZ]: Uploading geospatial data to space ID '{}'".format(space.info['id']))

    # Upload the geospatial data to the space
    space.add_features_geojson(file_path, encoding='utf-8', features_size=500, chunk_size=5)

    print("[HERE XYZ]: Successfully uploaded geospatial data to space ID '{}'".format(space.info['id']))
