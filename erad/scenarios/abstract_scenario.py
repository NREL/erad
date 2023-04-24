""" Module contains the base class defination for all scenarios.

Each scenario type will extend the base class to implement a given scenario
"""


from shapely.geometry import MultiPolygon, Polygon, LineString, Point
from datetime import datetime
from typing import *
import shapely

from erad.scenarios.common import AssetTypes

class BaseScenario:
    
    """Base class for scenario defination.

    Attributes:
        geodata (MultiPolygon, Point, LineString): Region of interest
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
        kwargs (dict): Additional parameters relevant for a particular scenario type
        
    """
    
    def __init__(self,  geodata : Union[MultiPolygon, Point, LineString] , probability_model : dict, timestamp : datetime, **kwargs) -> None:
        """Constructor for BaseScenario class.

        Args:
            geodata (MultiPolygon, Point, LineString): Region of interest
            probability_model (dict): Dictionary mapping asset types to probability funcitons
            timestamp (datetime): Scenario occurance time 
            kwargs (dict): Additional parameters relevant for a particular scenario type
        """
        if probability_model is None:
            probability_model = self.fragility_curves
        self.valitate_user_defined_fragility_curves(probability_model)
        
    
        if isinstance(geodata, Polygon):
           geodata = MultiPolygon([geodata]) 
        
        if isinstance(geodata, MultiPolygon):
            print("Is multipolygon")
            self.multipolygon = geodata
        elif isinstance(geodata, Point):
            print("Is point")
            self.origin = geodata
        elif isinstance(geodata, LineString):
            print("Is linestring")
            self.front = geodata
        else:
            print(geodata, Point)
            raise Exception(f"Invalid data type {type(geodata)}")
        
        self.probability_model = probability_model
        self.to_projection = f"epsg:{self.identify_stateplane_projection}"
        self.timestamp = timestamp
        return
    
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
        raise NotImplementedError("Method needs to be defined in derived classes")
    
    def increment_time(self) -> dict:
        """Method to increment simulation time for time evolviong scenarios."""
        raise NotImplementedError("Method needs to be defined in derived classes")

    def calculate_survival_probability(self, assets : dict, timestamp : datetime) -> dict:
        """Method to calculate survival probaility of asset types.

        Args:
            assets (dict): The dictionary of all assets and their corresponding asset types
        """
        raise NotImplementedError("Method needs to be defined in derived classes")

    def plot(self):
        """Method to plot survival probaility of in the region of interest"""
        raise NotImplementedError("Method needs to be defined in derived classes")
   
    def asset_survial_probability(self, asset_type):
        raise NotImplementedError("Method needs to be defined in derived classes")
    
    def valitate_user_defined_fragility_curves(self, distributions):
        for asset_type in distributions:
            assert AssetTypes.has_asset(asset_type), f"{asset_type} is not a valid asset type. Valid options are {list(AssetTypes.__members__.keys())}"
        return