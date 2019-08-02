"""geo.py

Felix van Oost 2019

Exports geographic data for all Strava activities in GeoJSON format.
"""

from geopandas import GeoDataFrame
import pandas
import polyline
from shapely.geometry import Point, LineString

# File paths
STRAVA_ACTIVITIES_MAP_FILE = 'Data/StravaActivitiesMap.geojson'

def decode_polyline(x):
    """
    Converts a Google polyline into a list of coordinates.
    """

    if x['polyline'] is not None:
        map_coordinates = polyline.decode(x['polyline'])
    else:
        map_coordinates = None    
    
    return map_coordinates

def create_shapely_point(coordinates):
    """
    Converts a pair of coordinates into a Shapely point.
    """

    return [Point(y, x) for x, y in coordinates]

def create_activities_map_file(activities_dataframe):
    """
    Creates a GeoJSON-encoded file of all Strava activities with geographic data.
    Contains the name, ID, type, distance, total elevation gain, and a LineString representing the map trace of each activity.
    """

    # Decode the activity polylines into coordinates
    print('Geo: Decoding activity polylines')
    activities_dataframe.loc[:, 'map_coordinates'] = activities_dataframe.loc[:, 'map'].apply(decode_polyline)

    # Create a new DataFrame containing only activities with geographic data
    activities_map_dataframe = activities_dataframe.loc[activities_dataframe.map_coordinates.isnull() == False, :].copy()

    # Convert the coordinates into Shapely points
    activities_map_dataframe.loc[:, 'map_points'] = activities_map_dataframe.loc[:,'map_coordinates'].apply(create_shapely_point)

    # Convert the Shapely points into LineStrings
    activities_map_dataframe.loc[:, 'map_linestring'] = activities_map_dataframe.loc[:, 'map_points'].apply(LineString)

    # Create a GeoDataFrame from the activities map DataFrame
    activities_map_geodataframe = GeoDataFrame(activities_map_dataframe[['name', 'id', 'type', 'distance', 'total_elevation_gain', 'map_linestring']], geometry = 'map_linestring')

    # Export the GeoDataFrame to a file in GeoJSON format
    print('Geo: Exporting map data to {}'.format(STRAVA_ACTIVITIES_MAP_FILE))
    activities_map_geodataframe.to_file(STRAVA_ACTIVITIES_MAP_FILE, driver = 'GeoJSON', encoding = 'utf8')
