# Strava Analysis Tool
A Python tool to analyse and display Strava activity data.

## Introduction
This tool aims to use the data collected by Strava to offer a new insight into your activities and workouts. Its original purpose was to create a personal activity heatmap (similar to the paid Strava feature for Summit members), but now encompasses a greater variety of data analysis and visualization options.

The full list of features and known issues is covered in the release notes for each tag.

## Installation

### 1. Python + Dependencies
The tool is developed with Python 3.7.4. Its depedencies are tracked in ```requirements.txt``` (for Pip) and ```spec-file.txt``` (for the [Anaconda](https://www.anaconda.com/distribution/) distribution).

Anaconda is recommended for Windows users as it comes pre-installed with many of the common packages required by the tool. It is also the preferred method to install ```GeoPandas```, which is leveraged for the processing and exporting of geospatial activity data. See the GeoPandas [Installation](http://geopandas.org/install.html) page for more information.

### 2. Strava API Access
The tool needs to be registered as an app with Strava to obtain access the Strava API. The steps to do this are outlined below:

1. From https://www.strava.com/settings/api, create a new application and set the 'Authorization Callback Domain' field to ```localhost```.
2. Copy the generated client ID and store it on your local machine as an environment variable named ```STRAVA_CLIENT_ID```. Repeat the process for the client secret and store it as an environment variable named  ```STRAVA_CLIENT_SECRET```.

The first time it is run, the tool will open a browser window and redirect to a Strava app permissions page. Click 'Authorize' to give the script access to your Strava data (this includes activities marked as 'private'). Note that only read permissions are requested; the tool is not capable of adding, modifying, or deleting any activities from your personal profile.

After authorizing access, the browser will redirect to an invalid page (```http://localhost```) and return an error. The returned URL, however, is still valid and contains the access token required for the tool to authenticate itself with the Strava API. The URL will be of the form:

```http://localhost/?state=&code=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&scope=read,activity:read_all```

When prompted by the tool, copy the ```code``` portion of the URL (```xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx```) and paste it in the console. It will use this code to obtain an initial set of OAuth2 tokens, which only needs to be done once.
