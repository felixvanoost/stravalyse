# Strava Analysis Tool
A Python tool to analyse and display Strava activity data.

## Introduction
The Strava Analysis Tool tool aims to use the data collected by Strava to offer a new insight into your activities and workouts. Its original purpose was to create a personal activity heatmap (similar to the paid Strava feature for Summit members), but now encompasses a greater variety of data analysis and visualization options.

A full list of features and known issues is covered in the notes for each release.

## Installation

### 1. Python + Dependencies
The tool is developed with Python 3.9. Its dependencies are tracked in `requirements.txt` (for Pip) and `environment.yml` (for the [Anaconda](https://www.anaconda.com/distribution/) distribution).

Anaconda is recommended for Windows users as it comes pre-installed with many of the required packages. It is also the preferred method for installing `GeoPandas`, which is leveraged for the processing and exporting of geospatial activity data. See the GeoPandas [Installation](http://geopandas.org/install.html) page for more information.

#### Option 1: Environment setup using Python

Create and activate a new virtual environment in Python using the commands:

```
python -m venv [path-to-environment]
python [path-to-environment]/bin/activate
```

Then install the required dependencies using:

```
pip install -r requirements.txt
```

#### Option 2: Environment setup using Anaconda

Create and activate a new environment in Anaconda with the required dependencies using the commands:

```
conda env create -f environment.yml
conda activate strava-analysis-tool-env
```

### 2. Strava API Access
The tool needs to be registered as an app with Strava to obtain access the Strava API. You can do this as follows:

1. From https://www.strava.com/settings/api, create a new application and set the 'Authorization Callback Domain' field to `localhost`.
2. Copy the generated client ID and store it on your local machine as an environment variable named `STRAVA_CLIENT_ID`. Do the same for the client secret and store it as an environment variable named `STRAVA_CLIENT_SECRET`.

When it is first run, the tool will open a browser window and redirect to a Strava app permissions page. Click 'Authorize' to give it access to your Strava data (this includes activities marked as 'private'). Note that only read permissions are requested; the tool is not capable of adding, modifying, or deleting any activities from your personal profile.

After authorizing access, the browser will redirect to an invalid page (`http://localhost`) and return an error. The returned URL, however, is still valid and contains the access code required for the tool to authenticate itself with the Strava API. The URL will be of the form:

`http://localhost/?state=&code=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&scope=read,activity:read_all`

When prompted, copy the `code` portion of the URL (`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) and paste it into the console. The tool will get and refresh its own OAuth2 tokens, so this only needs to be done once.

### 3. HERE account
You will need to register for a free HERE developer account if you want the tool to leverage the capabilities of the [HERE Studio](https://studio.here.com/) mapping platform. HERE Studio provides a very slick way to visualise your Strava data with a variety of map styles and customized formatting rules. Here's a basic example:

[![Demo Activity Map](Media/Demo%20Activity%20Map.JPG)](https://studio.here.com/viewer/?project_id=d99c795f-b247-47f9-a67e-972255a02017)

Once configured, the tool can automatically upload your Strava data to HERE to generate an up-to-date map of your activities. You can set rules to colour-code activities (by type or moving time, for instance) within the HERE Studio web app, and clicking on an activity will bring up some useful basic information (try it!).

After creating a developer account, generate a new access token with all permissions for all spaces using [this](https://xyz.api.here.com/token-ui/accessmgmt.html) link and copy the token into an environment variable named `XYZ_TOKEN`.

## Usage

Run the tool using the command:

`python strava_analysis_tool.py`

The following command line options are available:

| Command | Description |
| ------- | ------------|
| `-a / --activity_counts_plot` | Generate and display a plot of activity counts over time |
| `-c / --commute_plots` | Generate and display plots of the commute data |
| `-d / --mean_distance_plot` | Generate and display a plot of the mean activity distance over time |
| `-g / --export_geo_data` | Export the geospatial activity data in GeoJSON format |
| `-gu / --export_upload_geo_data` | Export the geospatial activity data in GeoJSON format and upload it to the HERE XYZ mapping platform |
| `-l / --start_locations_plot` | Generate and display a plot of the number of activities started in each country |
| `-m / --moving_time_heatmap` | Generate and display a heatmap of moving time for each activity type |
| `-r / --refresh_data` | Get and store a fresh copy of the activity data |
| `--date_range_start` | Specify the start of a date range in ISO format |
| `--date_range_end` | Specify the end of a date range in ISO format |

These options can also be displayed from within the command line using the help command:

`python strava_analysis_tool.py -h` or `python strava_analysis_tool.py --help`

All user-configurable parameters, such as file paths and the colour palette used to generate any plots, are stored in the file `config.toml`.

### Plots

From release v1.2.0 onwards, the tool is capable of generating some basic plots from your Strava data. The types of plots currently supported are described in the release notes, but here are some examples:

![Demo Activity Counts Plot](Media/Demo%20Activity%20Counts%20Plot.JPG)

![Demo Commute Plots](Media/Demo%20Commute%20Plots.JPG)

![Demo Mean Distance Plot](Media/Demo%20Mean%20Distance%20Plot.JPG)

![Demo Start Locations Plot](Media/Demo%20Start%20Locations%20Plot.jpeg)

![Demo Moving Time Heatmap Plot](Media/Demo%20Moving%20Time%20Heatmap.jpeg)
