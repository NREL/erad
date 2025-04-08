from erad.constants import FIRE_HISTORIC_GEODATAFRAME_PATH, DATA_FOLDER
from erad.scenarios.utilities import ProbabilityFunctionBuilder
from erad.constants import ERAD_DB, HISTROIC_FIRE_TABLE
from shapely import MultiPolygon, Point, LineString
from erad.scenarios.abstract_scenario import BaseScenario
from erad.exceptions import FeatureNotImplementedError
from erad.scenarios.utilities import GeoUtilities
from erad.scenarios.common import AssetTypes
import matplotlib.pyplot as plt
from datetime import datetime
import geopandas as gpd
import pandas as pd
import numpy as np
import sqlite3
import pyproj
import os

from shapely import wkb

from uuid import UUID
from enum import Enum
from pathlib import Path
import fiona

class FireSelection(str, Enum):
    UUID  = "uuid"
    NAME = "name"


class FireScenario(BaseScenario, GeoUtilities): 
    """Base class for FireScenario. Extends BaseScenario and GeoUtilities

    Attributes:
        multipolygon (MultiPolygon): MultiPolygon enclosing wild fire regions 
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
    """
    
    fragility_curves = {
        AssetTypes.substation.name : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.solar_panels.name :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.buried_lines.name :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.wind_turbines.name :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.battery_storage.name : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.transmission_poles.name  :   ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.distribution_poles.name  :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.transmission_overhead_lines.name  : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.distribution_overhead_lines.name  :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
    }
    
    def __init__(self,  multipolygon : MultiPolygon , probability_model : dict, timestamp : datetime) -> None:
        """Constructor for FireScenario.

        Args:
            multipolygon (MultiPolygon):  MultiPolygon enclosing wild fire regions 
            probability_model (dict): Dictionary mapping asset types to probability funcitons
            timestamp (datetime): Scenario occurance time 
        """
    
        super(FireScenario, self).__init__(multipolygon, probability_model, timestamp)     
        return      
    
    @staticmethod
    def fetch_historical_fire_data(fire_info: str|UUID, selection_mode: FireSelection):
        assert os.path.exists(ERAD_DB), f"The data file {ERAD_DB} not found"
        conn = sqlite3.connect(ERAD_DB)
        if selection_mode == FireSelection.NAME:
            assert isinstance(fire_info, str), "Fire name should be of type string"
            column_name= "firename"
        elif selection_mode == FireSelection.UUID:
            assert isinstance(fire_info, str), "Fire uuid should be of type string. Do not remove the brackets"
            column_name= "globalid"
        else:
            raise ValueError("Unsupported chose. Valid options are ['name', 'uuid']")
        
        fire_data = pd.read_sql(f"SELECT * FROM {HISTROIC_FIRE_TABLE} WHERE {column_name} = '{fire_info}';", conn)
        if fire_data.empty:
            raise ValueError(f"Fire '{fire_info}'  not found in column '{column_name}', table '{HISTROIC_FIRE_TABLE}' in the database")
 
        conn.close() 
        return fire_data
    
    @classmethod
    def from_dynamic_model(cls, multipolygon : MultiPolygon , probability_function : dict, timestamp : datetime):
        pass
    
    
    
    @classmethod
    def from_historical_fire_by_name(cls, fire_name : str, probability_function : dict = None):
        """Class method for FireScenario.

        Args:
            fire_code (str): Code for a historic wild fire event
            probability_function (dict): Dictionary mapping asset types to probability funcitons
        """
        fire_data = cls.fetch_historical_fire_data(fire_name, FireSelection.NAME)
        geometry = [wkb.loads(g) for g in fire_data.GEOMETRY]
        cls.fire_data = gpd.GeoDataFrame(fire_data, geometry=geometry) 
        print(cls.fire_data.T)
        cls.fire_data.set_crs('epsg:4326')
        multipolygon = cls.fire_data["geometry"].values[0]   
        timestamp = cls.fire_data["discoverydatetime"].values[0]
        return cls(multipolygon, probability_function, timestamp)
    
    @classmethod
    def from_historical_fire_by_uuid(cls, fire_uuid: UUID, probability_function : dict = None):
        """Class method for FireScenario.

        Args:
            fire_code (str): Code for a historic wild fire event
            probability_function (dict): Dictionary mapping asset types to probability funcitons
        """
        fire_data = cls.fetch_historical_fire_data(fire_uuid, FireSelection.UUID)
        geometry = [wkb.loads(g) for g in fire_data.GEOMETRY]
        cls.fire_data = gpd.GeoDataFrame(fire_data, geometry=geometry) 
        cls.fire_data.set_crs('epsg:4326')
        multipolygon = cls.fire_data["geometry"].values[0]   
        timestamp = cls.fire_data["discoverydatetime"].values[0]
        return cls(multipolygon, probability_function, timestamp)

    @property
    def area(self) -> float:
        """Method to calculate area of affected region."""
        geod = pyproj.Geod(ellps="WGS84")
        area = abs(geod.geometry_area_perimeter(self.polygon)[0])
        return area
    
    @property
    def polygon(self) -> MultiPolygon:
        """Method to return polygon for the affected region."""
        return self.multipolygon
        
    @property
    def boundary(self) -> LineString:
        """Method to return boundary for the affected region."""
        return self.multipolygon.boundary
        
    @property
    def centroid(self) -> Point:
        """Method to return the centroid of the affected region."""
        return self.polygon.centroid
            
    def increment_time(self):
        """Method to increment simulation time for time evolviong scenarios."""
        raise FeatureNotImplementedError()

    def calculate_survival_probability(self, assets : dict, timestamp : datetime, plot: bool) -> dict:
        """Method to calculate survival probaility of asset types.

        Args:
            assets (dict): The dictionary of all assets and their corresponding asset types
            plot (bool): Set to true to plot the fire survival model
        """
        if plot:
            points = []
        for asset_type, asset_dict in assets.items():
            assert asset_type in self.probability_model, f"Survival probability for asset type '{asset_type}' not found in the passed probability_model"
            probability_function = self.probability_model[asset_type]
            for asset_name, asset_ppty in asset_dict.items():
                coords = Point(asset_ppty["coordinates"])
                coords_flipped = Point(coords.y, coords.x)

                if self.in_polygon(coords_flipped):
                    distance = 0
                    survival_probability = 0
                else:
                    try:
                        distance = self.distance_from_boundary(coords)
                    except:
                        distance = self.distance_from_boundary(Point(coords.y, coords.x))
                    survival_probability = probability_function.probability(distance*1000)
                
                assets[asset_type][asset_name]["survival_probability"] = survival_probability
                assets[asset_type][asset_name]["distance_to_boundary"] = distance
                if plot:
                    points.append((coords.x, coords.y, survival_probability))
        if plot:
            points = np.array(points)
                    
            X = points[:,0]
            Y = points[:,1]
            Z = points[:,2]
                    
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_trisurf(X, Y, Z, color='white', edgecolors='grey', alpha=0.3)
            #ax.scatter(X, Y, Z, c='red')
            plt.show()
                
        return assets
                
    def plot(self):
        self.fire_data.plot()
        # plt.show()


