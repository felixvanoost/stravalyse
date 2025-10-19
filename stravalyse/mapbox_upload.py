"""mapbox_upload.py

Uploads Strava activity data to Mapbox.

Felix van Oost 2025
"""

# Standard library
import os
from pathlib import Path
import subprocess

# Third-party
from dotenv import load_dotenv
from mapbox import Uploader


def _create_tileset(geojson_file_path: Path, tileset_name: str, tileset_zoom_level: int) -> Path:
    """
    Process a GeoJSON file into a tileset using tippecanoe.

    Args:
        geojson_file: The path to the GeoJSON file.
        tileset_name: The name of the tileset to be created.
        tileset_zoom_level: The zoom level for the tileset.

    Returns:
        str: The path to the generated .mbtiles file.
    """

    print(f"Creating Mapbox tileset from {geojson_file_path}")
    tileset_path: Path = Path(geojson_file_path).parent / \
        f"{tileset_name}.mbtiles"

    # Run tippecanoe to create the tileset from the GeoJSON file.
    subprocess.run([
        'tippecanoe', '-o', tileset_path, f"-z{tileset_zoom_level}", '--drop-densest-as-needed',
        '--coalesce', '--force', geojson_file_path], check=True)

    return tileset_path


def _upload_tileset(tileset_path: Path, tileset_name: str) -> None:
    """
    Upload the generated .mbtiles file to Mapbox Studio.

    Args:
        tileset_path: The path of the Mapbox tileset (.mbtiles) file.
        tileset_name: The name of the tileset.
    """

    # Load the Mapbox access token from the .env file.
    load_dotenv()
    service = Uploader(access_token=os.environ.get('MAPBOX_TOKEN'))

    print(f"Uploading tileset '{tileset_name}' to Mapbox Studio")
    with open(tileset_path, 'rb') as file:
        upload_resp = service.upload(
            fileobj=file, tileset=tileset_name)
        print(upload_resp)


def upload_geo_data(geojson_file_path: Path, tileset_name: str, tileset_zoom_level: int) -> None:
    """
    Process the given GeoJSON file into a tileset and upload it to Mapbox Studio.

    Args:
        geojson_file_path: The path to the GeoJSON file.
        tileset_name: The name of the tileset.
        tileset_zoom_level: The zoom level for the tileset.
    """

    tileset_path: Path = _create_tileset(
        geojson_file_path, tileset_name, tileset_zoom_level)
    _upload_tileset(tileset_path, tileset_name)
