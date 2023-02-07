
import matplotlib.pyplot as plt
from scenarios.utilities import ProbabilityFunctionBuilder, GeoUtilities
from constants import FLOOD_HISTORIC_SHP_PATH, DATA_FOLDER
from shapely.geometry import MultiPolygon, Point, LineString
from scenarios.abstract_scenario import BaseScenario
from datetime import datetime
import geopandas as gpd
import pandas as pd
import numpy as np
import os


class FlooadScenario(BaseScenario, GeoUtilities):
    """Base class for FlooadScenario. Extends BaseScenario and GeoUtilities

    Attributes:
        origin (Point): Earthquake origin point
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
        kwargs (dict): Additional parameters relevant for a particular scenario type      
    """
    
    def __init__(self,  multipolygon : MultiPolygon , probability_model : dict, timestamp : datetime, **kwargs) -> None:
        super(FlooadScenario, self).__init__(multipolygon, probability_model, timestamp, **kwargs)
        self.kwargs = kwargs
        return
    
    @classmethod
    def from_dynamic_model(cls, multipolygon : MultiPolygon , probability_function : dict, timestamp : datetime):
        raise NotImplementedError("Method needs to be defined in derived classes")
    
    @classmethod
    def from_historical_flood_by_code(cls, flood_code : str, probability_function : dict):
        """Class method for EarthquakeScenario.

        Args:
            flood_code (str): Code for a historic flood event
            probability_function (dict): Dictionary mapping asset types to probability funcitons
        """
        
        data_file = os.path.join(DATA_FOLDER, FLOOD_HISTORIC_SHP_PATH)
        assert os.path.exists(data_file), f"The data file {data_file} not found"
        flood_data = gpd.read_file(data_file)
        cls.flood_data_filtered = flood_data[flood_data['dfirm_id'] == flood_code]
        assert not cls.flood_data_filtered.empty, f"Flood name '{flood_code}' not found in the database"
        print(cls.flood_data_filtered)
        cls.flood_data_filtered.drop('geometry',axis=1).to_csv(r'C:\Users\alatif\Documents\GitHub\erad\data\test.csv') 
        multipolygon = cls.flood_data_filtered["geometry"].values[0]   
        
        return cls(multipolygon, None, None)
   
    @property
    def area(self) -> float:
        """Method to calculate area of affected region."""
        raise NotImplementedError("Method needs to be defined in derived classes")
    
    @property
    def polygon(self) -> MultiPolygon:
        """Method to return polygon for the affected region."""
        raise NotImplementedError("Method needs to be defined in derived classes")
        
    @property
    def boundary(self) -> LineString:
        """Method to return boundary for the affected region."""
        raise NotImplementedError("Method needs to be defined in derived classes")
        
    @property
    def centroid(self) -> Point:
        """Method to return the centroid of the affected region."""
        return self.multipolygon.centroid
    
    def increment_time(self) -> dict:
        """Method to increment simulation time for time evolviong scenarios."""
        raise NotImplementedError("Method needs to be defined in derived classes")

    def calculate_survival_probability(self, assets : dict) -> dict:
        """Method to calculate survival probaility of asset types.

        Args:
            assets (dict): The dictionary of all assets and their corresponding asset types
        """
        raise NotImplementedError("Method needs to be defined in derived classes")
    
    def plot(self):
        self.flood_data_filtered.plot()
        plt.show()        
            

if __name__ == '__main__':
    flood_1 = FlooadScenario.from_historical_flood_by_code("01001C", None)
    flood_1.plot()
   