
import matplotlib.pyplot as plt
from erad.scenarios.utilities import ProbabilityFunctionBuilder, GeoUtilities
from erad.constants import EARTHQUAKE_HISTORIC_CSV_PATH, DATA_FOLDER
from shapely.geometry import MultiPolygon, Point, LineString
from erad.scenarios.abstract_scenario import BaseScenario
from datetime import datetime
import pandas as pd
import numpy as np
import os


class EarthquakeScenario(BaseScenario, GeoUtilities):
    """Base class for EarthquakeScenario. Extends BaseScenario and GeoUtilities

    Attributes:
        origin (Point): Earthquake origin point
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
        kwargs (dict): Additional parameters relevant for a particular scenario type      
    """
    
    def __init__(self,  origin : Point , probability_model : dict, timestamp : datetime, **kwargs) -> None:
        """Constructor for EarthquakeScenario.

        Args:
            origin (Point): Earthquake origin point
            probability_model (dict): Dictionary mapping asset types to probability funcitons
            timestamp (datetime): Scenario occurance time 
            kwargs (dict): Additional parameters relevant for a particular scenario type      
        """
        
        super(EarthquakeScenario, self).__init__(origin, probability_model, timestamp, **kwargs)
        self.kwargs = kwargs
        return
    
    @classmethod
    def from_dynamic_model(cls, origin : Point , probability_function : dict, timestamp : datetime):
        raise NotImplementedError("Method needs to be defined in derived classes")
    
    @classmethod
    def from_historical_earthquake_by_code(cls, earthquake_code : str, probability_function : dict):
        """Class method for EarthquakeScenario.

        Args:
            earthquake_code (str): Code for a historic eqrthquake event
            probability_function (dict): Dictionary mapping asset types to probability funcitons
        """
        
        data_file = os.path.join(DATA_FOLDER, EARTHQUAKE_HISTORIC_CSV_PATH)
        assert os.path.exists(data_file), f"The data file {data_file} not found"
        earthquake_data = pd.read_csv(data_file, index_col=None)
        earthquake_data['DateTime'] = pd.to_datetime(earthquake_data['Date'] + ' ' + earthquake_data['Time'], format='%m/%d/%Y %H:%M:%S')
        earthquake_data_filtered = earthquake_data[earthquake_data['ID'] == earthquake_code]
        
        timestamp = earthquake_data_filtered.DateTime.values[0]
        kwargs = {
            "Magnitude": earthquake_data_filtered.Magnitude.values[0],
            "Depth" : earthquake_data_filtered.Depth.values[0],
            }
        long = earthquake_data_filtered.Longitude.values[0]
        lat = earthquake_data_filtered.Latitude.values[0]
        origin = Point(long, lat) 
        return cls(origin, probability_function, timestamp, **kwargs)
    
    @property
    def centroid(self):
        """Method to return the centroid of the affected region."""
        return self.origin
    
    def increment_time(self):
        """Method to increment simulation time for time evolviong scenarios."""
        raise NotImplementedError("Method needs to be defined in derived classes")

    def calculate_survival_probability(self, assets : dict) -> dict:
        """Method to calculate survival probaility of asset types.

        Args:
            assets (dict): The dictionary of all assets and their corresponding asset types
        """
        
        for asset_type, asset_dict in assets.items():
            # assert asset_type in self.probability_model, f"Survival probability for asset type '{asset_type}' not found in the passed probability_model"
            # probability_function = self.probability_model[asset_type]
            for asset_name, asset_ppty in asset_dict.items():
                coords = Point(asset_ppty["coordinates"])
                coords_flipped = Point(coords.y, coords.x)
            
                epicenter_distance = self.distance_from_centroid(coords)
                depth = self.kwargs["Depth"]
                magnitude = self.kwargs["Magnitude"]
                
                hypocentral_distance = (depth**2 + epicenter_distance**2)**0.5
                intensity = 0.66* magnitude - 1.13 * np.log(hypocentral_distance) -0.0072 * hypocentral_distance + 3.73
                act_int = 10**intensity
                survival_prob = 1 - act_int / 383641.228284058
                if  survival_prob > 1:
                    survival_prob = 1
                elif survival_prob < 0:
                    survival_prob = 0
                
                assets[asset_type][asset_name]["survival_probability"] = survival_prob
        return assets

    def plot(self, d : float):
        """Method to plot survival probaility of in the region of interest"""
        m = range(2, 10)
        h = np.linspace(14, 70, 100)
       
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for magnitude in m:
            points = []
            for depth in h:
                hypocentral_distance = (depth**2 + d**2)**0.5
                intensity = 0.66* magnitude - 1.13 * np.log(hypocentral_distance) -0.0072 * hypocentral_distance + 3.73
                act_int = 10**intensity
                survival_prob = 1 - act_int / 383641.228284058
                if  survival_prob > 1:
                    survival_prob = 1
                elif survival_prob < 0:
                    survival_prob = 0
                
                points.append(survival_prob)
                
            print(points[0])
            ax.plot(h, points, label=f"magnitude: {magnitude}")
            ax.legend()
        plt.show()
            
            

if __name__ == '__main__':
    earthquake_1 = EarthquakeScenario.from_historical_earthquake_by_code("USP000GYZK", None)
    earthquake_1.plot(30)
   