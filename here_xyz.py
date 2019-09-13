"""here_xyz.py

Uploads and manages geospatial data from Strava activities with the HERE
XYZ mapping platform.

Functions:

Felix van Oost 2019
"""

# Local imports
import subprocess


def get_space_id() -> str:
    """
    Get and return the ID of the space containing the Strava activity
    data or create a new space if one does not currently exist.

    Return:
    The ID of the space containing the Strava activity data.
    """

    space_id = None

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
            break
    
    if not space_id:
        # Create a new space
        process = subprocess.Popen(['here', 'xyz', 'create', '-t', 'Strava Activity Data', '-d',
                                    'Created by Strava Heatmap Tool'],
                                   shell=True, stdout=subprocess.PIPE, universal_newlines=True)
        output = process.stdout.readline()
        space_id = output.split()[1]

    return space_id