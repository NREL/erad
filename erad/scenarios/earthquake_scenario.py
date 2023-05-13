
import matplotlib.pyplot as plt
from erad.scenarios.utilities import ProbabilityFunctionBuilder, GeoUtilities
from erad.constants import EARTHQUAKE_HISTORIC_CSV_PATH, DATA_FOLDER
from shapely.geometry import MultiPolygon, Point, LineString
from erad.scenarios.abstract_scenario import BaseScenario
from erad.scenarios.common import asset_list
from datetime import datetime
import pandas as pd
import numpy as np
import math
import os

from erad.scenarios.common import AssetTypes
from erad.scenarios.utilities import ProbabilityFunctionBuilder

class EarthquakeScenario(BaseScenario, GeoUtilities):
    """Base class for EarthquakeScenario. Extends BaseScenario and GeoUtilities

    Attributes:
        origin (Point): Earthquake origin point
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
        kwargs (dict): Additional parameters relevant for a particular scenario type      
    """
    fragility_curves = {
            # Hierarchical seismic vulnerability assessment of power transmission systems: sensitivity analysis of fragility curves and clustering algorithms
            AssetTypes.substation.name : ProbabilityFunctionBuilder("norm", [0.75, 0.20]),
            # AssetTypes.solar_panels.name : ProbabilityFunctionBuilder("norm", [85, 10]),
            # Seismic performance of buried electrical cables: evidence-based repair rates and fragility functions
            # SEISMIC FRAGILITY OF UNDERGROUND ELECTRICAL CABLES IN THE 2010-11 CANTERBURY (NZ) EARTHQUAKES
            # AssetTypes.buried_lines.name : ProbabilityFunctionBuilder("uniform", [0, 1]),
            # Seismic Fragility Analysis of Monopile Offshore Wind Turbines under Different Operational Conditions
            AssetTypes.wind_turbines.name : ProbabilityFunctionBuilder("norm", [0.62, 0.17]),        
            # AssetTypes.battery_storage.name : ProbabilityFunctionBuilder("norm", [85, 10]),
            # Multi-hazard typhoon and earthquake collapse fragility models for transmission towers: An active learning reliability approach using gradient boosting classifiers
            AssetTypes.transmission_poles.name  :  ProbabilityFunctionBuilder("norm", [1.5, 0.45]),
            # Seismic performance and fragility analysis of power distribution concrete poles
            # AssetTypes.distribution_poles.name  : ProbabilityFunctionBuilder("norm", [0.73, 0.15]),
            #Improving the resilience of distribution network in coming across seismic damage using mobile battery energy storage system
            AssetTypes.distribution_poles.name  : ProbabilityFunctionBuilder("norm", [0.6, 0.12]),
            # https://www.researchgate.net/figure/Fragility-curves-that-show-the-probability-of-electric-power-lines-being-in-each-failure_fig3_339017910
            AssetTypes.transmission_overhead_lines.name  : ProbabilityFunctionBuilder("norm", [0.72, 0.1]),   
            # https://www.fema.gov/sites/default/files/2020-10/fema_hazus_earthquake_technical_manual_4-2.pdf
            AssetTypes.distribution_overhead_lines.name  : ProbabilityFunctionBuilder("lognorm", [0.3, 0.25,0.4]),
            
        }
    
    intensity_map = LineString([[1, 2.5], [2, 3.0], [3, 3.5], [4, 4.0], [5, 4.5], [6, 5.0], [7, 5.5], [8, 6.0], [9, 6.5], [10, 7.0], [11, 7.5], [12, 8.0]])
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
    def from_historical_earthquake_by_code(cls, earthquake_code : str, probability_function : dict= None):
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

    def calculate_survival_probability(self, assets : dict, timestamp : datetime) -> dict:
        """Method to calculate survival probaility of asset types.

        Args:
            assets (dict): The dictionary of all assets and their corresponding asset types
        """
        for asset_type, asset_dict in assets.items():
            # assert asset_type in self.probability_model, f"Survival probability for asset type '{asset_type}' not found in the passed probability_model"
            if asset_type in self.probability_model:
                
                probability_function = self.probability_model[asset_type]
                for asset_name, asset_ppty in asset_dict.items():
                    coords = Point(asset_ppty["coordinates"][::-1])
                    
                    epicenter_distance = self.distance_from_centroid(coords)
        
                    depth = self.kwargs["Depth"]
                    magnitude = self.kwargs["Magnitude"]

                    # Valutazione speditiva di sicurezza sismica degli edifici esistenti
                    hypocentral_distance = (depth**2 + epicenter_distance**2)**0.5
                    l = LineString([[0, magnitude], [100, magnitude]])
                    p = self.intensity_map.intersection(l)
                    Imcs = p.xy[0][0]
                    intensity = Imcs + 3 - 4.3 * math.log10(hypocentral_distance)
                    intensity = 0 if intensity < 0 else intensity
                    pga = 10**((intensity /3) - 1) / 9.81
                    probility =  1- probability_function.probability(pga)
                    assets[asset_type][asset_name]["survival_probability"] = probility
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
            
            

