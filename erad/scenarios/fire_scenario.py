from constants import FIRE_HISTORIC_GEODATAFRAME_PATH, DATA_FOLDER
from shapely.geometry import MultiPolygon, Point, LineString
from scenarios.utilities import ProbabilityFunctionBuilder
from scenarios.abstract_scenario import BaseScenario
from exceptions import FeatureNotImplementedError
from scenarios.utilities import GeoUtilities
import matplotlib.pyplot as plt
from datetime import datetime
import geopandas as gpd
import numpy as np
import pyproj
import os

class FireScenario(BaseScenario, GeoUtilities): 
    """Base class for FireScenario. Extends BaseScenario and GeoUtilities

    Attributes:
        multipolygon (MultiPolygon): MultiPolygon enclosing wild fire regions 
        probability_model (dict): Dictionary mapping asset types to probability funcitons
        timestamp (datetime): Scenario occurance time 
    """
    
    def __init__(self,  multipolygon : MultiPolygon , probability_model : dict, timestamp : datetime) -> None:
        """Constructor for FireScenario.

        Args:
            multipolygon (MultiPolygon):  MultiPolygon enclosing wild fire regions 
            probability_model (dict): Dictionary mapping asset types to probability funcitons
            timestamp (datetime): Scenario occurance time 
        """
        
        
        super(FireScenario, self).__init__(multipolygon, probability_model, timestamp)     
        return
    
    @classmethod
    def from_dynamic_model(cls, multipolygon : MultiPolygon , probability_function : dict, timestamp : datetime):
        pass
    
    @classmethod
    def from_historical_fire_by_code(cls, fire_code : str, probability_function : dict):
        """Class method for FireScenario.

        Args:
            fire_code (str): Code for a historic wild fire event
            probability_function (dict): Dictionary mapping asset types to probability funcitons
        """
        
        data_file = os.path.join(DATA_FOLDER, FIRE_HISTORIC_GEODATAFRAME_PATH)
        assert os.path.exists(data_file), f"The data file {data_file} not found"
        fire_data = gpd.read_file(data_file)
        fire_data_longlat = fire_data.to_crs('epsg:4326')

        cls.fire_data_filtered = fire_data_longlat[fire_data_longlat['Combined_Fire_Code'] == fire_code]
        assert not cls.fire_data_filtered.empty, f"Fire name '{fire_code}' not found in the database"
        assert len(cls.fire_data_filtered) == 1, f"More than one record matched. Use additional filters for a unique match."
        multipolygon = cls.fire_data_filtered["geometry"].values[0]   
        timestamp = cls.fire_data_filtered["Combined_Ignition_Date"].values[0]
        if not np.datetime64:
            timestamp = cls.fire_data_filtered["Combined_Controlled_Date"].values[0]
            if not np.datetime64:
                timestamp = cls.fire_data_filtered["Combined_Containment_Date"].values[0]
        
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

    def calculate_survival_probability(self, assets : dict, plot: bool) -> dict:
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
                    survival_probability = probability_function(distance)
                
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
        self.fire_data_filtered.plot()
        plt.show()



if __name__ == '__main__':
    samples = 100
    
    x = np.linspace(41.255, 41.423, samples)
    y = np.linspace(-117.33, -117.55, samples)
    
    assets = {"overhead_power_lines" : {}}
    
    asset_id = 0
    for x1 in x:
        for y1 in y:
            assets["overhead_power_lines"][f"asset {asset_id}"] = {"coordinates" : (x1, y1)}
            asset_id += 1
             
    prob_model = ProbabilityFunctionBuilder("norm", [4, 0.5])    
    
    survival_model = {
        "overhead_power_lines" : prob_model.survival_probability
    }
    
    Fire1 = FireScenario.from_historical_fire_by_code("GHP4", survival_model)
    assets = Fire1.calculate_survival_probability(assets, True)
    print(assets)
    Fire1.plot()