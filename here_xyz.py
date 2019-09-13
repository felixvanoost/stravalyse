"""here_xyz.py

Uploads and manages the geospatial data from Strava activities with the
HERE XYZ mapping platform.

Functions:
upload_geo_data()

Felix van Oost 2019
"""

# Local imports
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
    process = subprocess.Popen(['here', 'xyz', 'list'],
                               shell=True, stdout=subprocess.PIPE, universal_newlines=True)

    # Check whether a 'Strava Activity Data' space already exists
    while True:
        line = process.stdout.readline()
        if not line:
            break
        elif 'Strava Activity Data' in line:
            space_id = line.split()[0]
            print('HERE XYZ: Found space with ID "{}"'.format(space_id))
            break

    if not space_id:
        print('HERE XYZ: No existing space found')

        # Create a new space
        process = subprocess.Popen(['here', 'xyz', 'create', '-t', 'Strava Activity Data', '-d',
                                   'Created by Strava Heatmap Tool'],
                                   shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.communicate()
        space_id = str(output).split()[1]
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
    process = subprocess.Popen(['here', 'configure', 'verify'],
                               shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.communicate()[0]

    if not output:
        # Get the ID of the space containing the geospatial activity data 
        space_id = _get_space_id()

        # Clear the space to prevent conflicts in overwriting existing data
        print('HERE XYZ: Clearing space ID "{}"'.format(space_id))
        process = subprocess.Popen(['here', 'xyz', 'clear', space_id.replace("'", "")],
                                shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                universal_newlines=True)
        output = process.communicate(input='Y')[0]

        if 'data cleared successfully' in output:
            # Upload the geospatial data to the space
            print('HERE XYZ: Uploading geospatial data to space ID "{}"'.format(space_id))
            process = subprocess.Popen(['here', 'xyz', 'upload', space_id, '-f', file_path,
                                    '-i', 'ID'],
                                    shell=True, stdout=subprocess.PIPE, universal_newlines=True)
            output = process.communicate()[0]

            if 'data upload to xyzspace' in output:
                print('HERE XYZ: Geospatial data successfully uploaded to space ID "{}"'.format(space_id))
            else:
                print('HERE XYZ: Error uploading geospatial data to space ID "{}"'.format(space_id))
        else:
            print('HERE XYZ: Error clearing space ID "{}"'.format(space_id))
    else:
        print('Error: Configure HERE CLI using the "here configure" command')
