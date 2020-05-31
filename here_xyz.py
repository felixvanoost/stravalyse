"""here_xyz.py

Uploads and manages the geospatial data from Strava activities with the
HERE XYZ mapping platform.

Functions:
upload_geo_data()

Felix van Oost 2019
"""

# Standard library
import shutil
import subprocess


def _get_space_id() -> str:
    """
    Get and return the ID of the space containing the Strava activity
    data or create a new space if one does not currently exist.

    Return:
    The ID of the space containing the Strava activity data.
    """

    space_id = None

    print('HERE XYZ: Locating the Strava activity data space')

    # Get a list of existing spaces
    command = [shutil.which('here'), 'xyz', 'list']
    for line in subprocess.check_output(command).decode('utf-8').split('\n'):
        # Check whether a 'Strava Activity Data' space already exists
        if 'Strava Activity Data' in line:
            space_id = line.split()[1]
            print('HERE XYZ: Found space with ID "{}"'.format(space_id))
            break

    if not space_id:
        print('HERE XYZ: No existing space found')

        # Create a new space
        command = [shutil.which('here'), 'xyz', 'create', '-t', '"Strava Activity Data"', '-d',
                   '"Created by Strava Analysis Tool"']
        space_id = subprocess.check_output(command).decode('utf-8').split()[2]
        print('HERE XYZ: Created new space with ID "{}"'.format(space_id))

    return space_id


def upload_geo_data(file_path: str):
    """
    Upload the geospatial data from Strava activities to the HERE XYZ
    mapping platform.

    Arguments:
    file_path - The path of the file containing the geospatial activity
                data.
    """

    # Check whether the HERE CLI has been properly configured.
    # The CLI will return an empty line if the HERE account information
    # has been validated.
    command = [shutil.which('here'), 'configure', 'verify']
    configure_verify_output = subprocess.check_output(command).decode('utf-8')

    if not configure_verify_output:
        # Get the ID of the space containing the geospatial activity data
        space_id = _get_space_id()

        # Clear the space to prevent conflicts in overwriting existing data
        print('HERE XYZ: Clearing space ID "{}"'.format(space_id))
        process = subprocess.Popen([shutil.which('here'), 'xyz', 'clear', space_id],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   universal_newlines=True)
        process.stdout.reconfigure(encoding='utf-8')
        clear_space_output, _ = process.communicate(input='Y')

        if 'data cleared successfully' in clear_space_output:
            # Upload the geospatial data to the space
            print('HERE XYZ: Uploading geospatial data to space ID "{}"'.format(space_id))
            command = ([shutil.which('here'), 'xyz', 'upload', space_id, '--file', file_path,
                       '--stream', '--id', '"id"', '--date', '"local start date"', '--datetag',
                       'year,month,weekday'])
            upload_output = subprocess.check_output(command).decode('utf-8')
            print('HERE XYZ: ' + upload_output)

            if not 'features uploaded to XYZ space' in upload_output:
                print('HERE XYZ: Error uploading geospatial data to space ID "{}"'.format(space_id))
        else:
            print('HERE XYZ: Error clearing space ID "{}"'.format(space_id))
    else:
        print('Error: Configure HERE CLI using the "here configure" command')
