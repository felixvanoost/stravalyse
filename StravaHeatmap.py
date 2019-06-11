"""StravaHeatmap.py

Felix van Oost 2019

This tool generates a heatmap of Strava activities using the HERE XYZ mapping service.
"""
import os
import strava_auth
import sys

# Add the folder containing the Strava Swagger API to the system path
sys.path.append(os.path.abspath('API'))

import swagger_client
from swagger_client.rest import ApiException

# Main module
if __name__ == "__main__":

    strava_auth.authenticate()