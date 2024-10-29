from erad.constants import FIRE_HISTORIC_GEODATAFRAME_PATH, DATA_FOLDER
from shapely.geometry import MultiPolygon, Point, LineString
from erad.scenarios.utilities import ProbabilityFunctionBuilder
from erad.scenarios.abstract_scenario import BaseScenario
from erad.exceptions import FeatureNotImplementedError
from erad.scenarios.utilities import GeoUtilities
import matplotlib.pyplot as plt
from datetime import datetime
import geopandas as gpd
import numpy as np
import random
import pyproj
import os

from erad.scenarios.common import AssetTypes
from erad.scenarios.utilities import ProbabilityFunctionBuilder


class WindScenario(BaseScenario, GeoUtilities): 
    """Base class for FireScenario. Extends BaseScenario and GeoUtilities

    Attributes:
        multipolygon (MultiPolygon): MultiPolygon enclosing wild fire regions 
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
    """
    
    fragility_curves = {
        #Extending energy system modelling to include extreme weather risks and application to hurricane events in Puerto Rico
        AssetTypes.substation.name : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.solar_panels.name :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.buried_lines.name :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.wind_turbines.name :  ProbabilityFunctionBuilder("norm", [0.8, 10, 5]),
        #AssetTypes.battery_storage.name : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        #AssetTypes.transmission_poles.name  :   ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.distribution_poles.name  :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
       # AssetTypes.transmission_overhead_lines.name  : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.distribution_overhead_lines.name  :  ProbabilityFunctionBuilder("beta", [0.8, 10, 5]),
    }
    
    def __init__(self,  multipolygon : MultiPolygon , probability_model : dict, timestamp : datetime) -> None:
        """Constructor for FireScenario.

        Args:
            multipolygon (MultiPolygon):  MultiPolygon enclosing wild fire regions 
            probability_model (dict): Dictionary mapping asset types to probability funcitons
            timestamp (datetime): Scenario occurance time 
        """

        super(WindScenario, self).__init__(multipolygon, probability_model, timestamp)     
        return      
    
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
        return assets
                


