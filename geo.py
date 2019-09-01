"""geo.py

Exports geospatial data for all Strava activities in GeoJSON format.

Functions:
export_geo_data_file()

Felix van Oost 2019
"""

# Third-party imports
from geopandas import GeoDataFrame
import pandas
import polyline
from shapely.geometry import Point, LineString

# File paths
STRAVA_GEO_DATA_FILE = 'Data/StravaGeoData.geojson'

def _decode_polyline(x: pandas.Series) -> list:
    """
    Convert a Google polyline into a list of coordinates.

    Arguments:
    A Google polyline as a pandas Series.

    Return:
    A list of decoded coordinates from the polyline.
    """

    if x['polyline'] is not None:
        map_coordinates = polyline.decode(x['polyline'])
    else:
        map_coordinates = None    
    
    return map_coordinates

def _create_shapely_point(coordinates: pandas.Series) -> Point:
    """
    Convert a pair of coordinates into a Shapely point.

    Arguments:
    A pair of coordinates as a pandas Series.

    Return:
    A Shapely point representing the coordinates.
    """

    return [Point(y, x) for x, y in coordinates]

def export_geo_data_file(activity_dataframe: pandas.DataFrame):
    """
    Export a GeoJSON-encoded file of geospatial data from all activities.

    The exported file contains the name, ID, type, distance, total
    elevation gain, and a LineString representing the trace of each
    activity.

    Arguments:
    activity_dataframe - A pandas DataFrame containing the activity data.
    """

    print('Geo: Processing geospatial data')

    # Convert the activity polylines into coordinates
    activity_dataframe.loc[:, 'map_coordinates'] = (activity_dataframe.loc[:, 'map']
        .apply(_decode_polyline))

    # Create a new DataFrame containing only activities with geospatial
    # data
    activity_map_dataframe = (activity_dataframe.loc[activity_dataframe.map_coordinates
        .isnull() == False, :].copy())

    # Convert the coordinates into Shapely points
    activity_map_dataframe.loc[:, 'map_points'] = (activity_map_dataframe.loc[:,'map_coordinates']
        .apply(_create_shapely_point))

    # Convert the Shapely points into LineStrings
    activity_map_dataframe.loc[:, 'map_linestring'] = (activity_map_dataframe.loc[:, 'map_points']
        .apply(LineString))

    # Convert the activity distances from m to km
    activity_map_dataframe.loc[:, 'distance'] = activity_map_dataframe.loc[:, 'distance'] / 1000

    # Create a pandas GeoDataFrame from the activities map DataFrame and
    # format the column names
    activity_map_geodataframe = GeoDataFrame(activity_map_dataframe[['name',
                                                                     'id',
                                                                     'type',
                                                                     'start_date_local_formatted',
                                                                     'distance',
                                                                     'moving_time_formatted',
                                                                     'total_elevation_gain',
                                                                     'map_linestring']],
                                                                     geometry='map_linestring')
    activity_map_geodataframe.rename(columns={'name': 'Name',
                                              'id': 'ID',
                                              'type': 'Type',
                                              'start_date_local_formatted': 'Start date',
                                              'distance': 'Distance (km)',
                                              'moving_time_formatted': 'Moving time',
                                              'total_elevation_gain': 'Total elevation gain (m)'},
                                              inplace=True)

    # Export the GeoDataFrame to a file in GeoJSON format
    print('Geo: Exporting geospatial data to {}'.format(STRAVA_GEO_DATA_FILE))
    activity_map_geodataframe.to_file(STRAVA_GEO_DATA_FILE, driver='GeoJSON', encoding='utf8')
