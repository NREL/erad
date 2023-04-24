""" Module for managing constants in ERAD package.

_Do not change this constants in your code._
"""

import os

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FOLDER_NAME = "data"
DATA_FOLDER = os.path.join(ROOT_PATH, DATA_FOLDER_NAME)

FIRE_HISTORIC_GEODATAFRAME_PATH = "US_Wildfires_1878_2019.gdb"
EARTHQUAKE_HISTORIC_CSV_PATH = "World_Earthquakes_1960_2016.csv"
FLOOD_HISTORIC_SHP_PATH = "FEMA_100_Year_Flood_Zones_in_the_US\\FEMA_100_Year_Flood_Zones_in_the_US.shp"
#FLOOD_HISTORIC_SHP_PATH = "NFHL_06_20230323.gdb"
ELEVATION_RASTER_FILE = "TrueMarble.250m.21600x21600.B2.tif"

SMARTDS_VALID_YEARS = [2016, 2017, 2018]
SMARTDS_VALID_AREAS = ['SFO', 'GSO', 'AUS']

