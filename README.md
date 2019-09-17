# Strava Analysis Tool
A Python tool to analyse and display Strava activity data.

## Introduction
The Strava Analysis Tool tool aims to use the data collected by Strava to offer a new insight into your activities and workouts. Its original purpose was to create a personal activity heatmap (similar to the paid Strava feature for Summit members), but now encompasses a greater variety of data analysis and visualization options.

A full list of features and known issues is covered in the notes for each release.

## Installation

### 1. Python + Dependencies
The tool is developed with Python 3.7. Its dependencies are tracked in `requirements.txt` (for Pip) and `spec-file.txt` (for the [Anaconda](https://www.anaconda.com/distribution/) distribution).

Anaconda is recommended for Windows users as it comes pre-installed with many of the required packages. It is also the preferred method for installing `GeoPandas`, which is leveraged for the processing and exporting of geospatial activity data. See the GeoPandas [Installation](http://geopandas.org/install.html) page for more information.

### 2. Strava API Access
The tool needs to be registered as an app with Strava to obtain access the Strava API. You can do this as follows:

1. From https://www.strava.com/settings/api, create a new application and set the 'Authorization Callback Domain' field to `localhost`.
2. Copy the generated client ID and store it on your local machine as an environment variable named `STRAVA_CLIENT_ID`. Do the same for the client secret and store it as an environment variable named `STRAVA_CLIENT_SECRET`.

When it is first run, the tool will open a browser window and redirect to a Strava app permissions page. Click 'Authorize' to give it access to your Strava data (this includes activities marked as 'private'). Note that only read permissions are requested; the tool is not capable of adding, modifying, or deleting any activities from your personal profile.

After authorizing access, the browser will redirect to an invalid page (`http://localhost`) and return an error. The returned URL, however, is still valid and contains the access code required for the tool to authenticate itself with the Strava API. The URL will be of the form:

`http://localhost/?state=&code=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&scope=read,activity:read_all`

When prompted, copy the `code` portion of the URL (`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) and paste it into the console. The tool will get and refresh its own OAuth2 tokens, so this only needs to be done once.

### 3. HERE CLI (Optional)
You will need to register for a free HERE account and install the [HERE CLI](https://github.com/heremaps/here-cli) if you want the tool to leverage the capabilities of the [HERE XYZ](https://xyz.here.com/) mapping platform. HERE XYZ provides a very slick way to visualise your Strava data with a variety of map styles and customized formatting rules. Here's a basic example:

[![Demo Activity Map](Media/Demo%20Activity%20Map.JPG)](https://xyz.here.com/viewer/?project_id=d99c795f-b247-47f9-a67e-972255a02017)

Once configured, the tool can automatically upload your Strava data to HERE XYZ to generate an up-to-date map of your activities. You can set rules to colour-code activities (by type or moving time, for instance) within HERE Studio, and clicking on an activity will bring up some useful basic information (try it!).

# Usage

Run the tool using the command:

`python run.py`

The following command line options are available:

| Command | Description |
| ------- | ------------|
| `-r / --refresh_data` | Get and store a fresh copy of the activity data |
| `-g / --export_geo_data` | Export the geospatial activity data in GeoJSON format |
| `-gu / --export_upload_geo_data` | Export the geospatial activity data in GeoJSON format and upload it to the HERE XYZ mapping platform |

These options can also be displayed from within the command line using the help command: 

`python run.py -h` or `python run.py --help`
