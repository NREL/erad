""" Module for managing constants in ERAD package.

_Do not change this constants in your code._
"""
from pathlib import Path
import os


ROOT_PATH = Path(__file__).parent.parent.parent
TEST_PATH = Path(__file__).parent.parent.parent / "tests"
DATA_FOLDER_NAME = "data"
DATA_FOLDER = TEST_PATH / DATA_FOLDER_NAME

ERAD_DB = TEST_PATH / DATA_FOLDER_NAME / "erad_data.sqlite"
HISTROIC_EARTHQUAKE_TABLE = "historic_earthquakes"
HISTROIC_HURRICANE_TABLE = "historic_hurricanes"
HISTROIC_FIRE_TABLE = "historic_fires"

FIRE_HISTORIC_GEODATAFRAME_PATH = "ContiguousUS_Wildfire_Rasters.gdb" #"US_Wildfires_1878_2019.gdb"
EARTHQUAKE_HISTORIC_CSV_PATH = "World_Earthquakes_1960_2016.csv"
FLOOD_HISTORIC_SHP_PATH = "FEMA_100_Year_Flood_Zones_in_the_US\\FEMA_100_Year_Flood_Zones_in_the_US.shp"
#FLOOD_HISTORIC_SHP_PATH = "NFHL_06_20230323.gdb"
ELEVATION_RASTER_FILE = "land_shallow_topo_west.tif"

SMARTDS_VALID_YEARS = [2016, 2017, 2018]
SMARTDS_VALID_AREAS = ['SFO', 'GSO', 'AUS']

