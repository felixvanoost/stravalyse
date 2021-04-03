"""here_xyz.py

Uploads and manages the geospatial data from Strava activities with the
HERE XYZ mapping platform.

Functions:
upload_geo_data()

Felix van Oost 2019
"""

# Standard library
import os
import shutil
import subprocess
import sys
import xyzspaces


def _get_space_id(xyz) -> str:
    """
    Get and return the ID of the space containing the Strava activity
    data or create a new space if one does not currently exist.

    Return:
    The ID of the space containing the Strava activity data.
    """

    space_id = None

    print('[HERE XYZ]: Locating the Strava activity data space')

    # Get a list of existing spaces
    spaces = xyz.spaces.list(owner='me')

    # Search for an existing space with the name 'Strava Activity Data'
    for space in spaces:
        if space['title'] == 'Strava Activity Data':
            space_id = space['id']
            print("[HERE XYZ]: Found space with ID '{}'".format(space_id))
            break

    if not space_id:
        print('[HERE XYZ]: No existing space found')

        # Create a new space
        space = xyz.spaces.new(title='Strava Activity Data',
                               description='Created by Strava Analysis Tool')
        space_id = space.info['id']

        print("[HERE XYZ]: Created new space with ID '{}'".format(space_id))

    return space_id


def upload_geo_data(file_path: str):
    """
    Upload the geospatial data from Strava activities to the HERE XYZ
    mapping platform.

    Arguments:
    file_path - The path of the file containing the geospatial activity
                data.
    """

    try:
        xyz_token = os.environ['XYZ_TOKEN']
    except KeyError:
        sys.exit('[ERROR]: Add XYZ_TOKEN to your environment variables')

    xyz = xyzspaces.XYZ(credentials=xyz_token)

    # Get the ID of the space containing the geospatial activity data
    space_id = _get_space_id(xyz)

    # Clear the space to prevent conflicts in overwriting existing data
    print('HERE XYZ: Clearing space ID "{}"'.format(space_id))
    process = subprocess.Popen([shutil.which('here'), 'xyz', 'clear', space_id],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
    clear_space_output, _ = process.communicate(input='Y')

    if 'data cleared successfully' in clear_space_output:
        # Upload the geospatial data to the space
        print('HERE XYZ: Uploading geospatial data to space ID "{}"'.format(space_id))
        command = ([shutil.which('here'), 'xyz', 'upload', space_id, '--file', file_path,
                    '--stream', '--id', '"id"', '--date', '"local start date"', '--datetag',
                    'year,month,weekday'])
        upload_output = subprocess.check_output(command).decode('utf-8')
        print('HERE XYZ: ' + upload_output)

        if not 'upload completed successfully' in upload_output:
            print('HERE XYZ: Error uploading geospatial data to space ID "{}"'.format(space_id))
    else:
        print('HERE XYZ: Error clearing space ID "{}"'.format(space_id))
