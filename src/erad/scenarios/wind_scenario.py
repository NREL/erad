from erad.scenarios.utilities import ProbabilityFunctionBuilder
from erad.constants import HISTROIC_HURRICANE_TABLE, ERAD_DB
from erad.scenarios.abstract_scenario import BaseScenario
from erad.exceptions import FeatureNotImplementedError
from shapely import MultiPolygon, Point, LineString
from erad.scenarios.utilities import GeoUtilities
from pydantic import BaseModel
from datetime import datetime
import geopandas as gpd
import pandas as pd
import sqlite3
import pyproj
import os

from erad.scenarios.common import AssetTypes
from erad.scenarios.utilities import ProbabilityFunctionBuilder



class HurricaneStatus(BaseModel):
    timestamp: datetime
    wind_speed_mph: float
    pressure_mb: float
    longitude: float
    latitude: float
    landfall_mi: float

class Hurricane(BaseModel):
    sid: str
    name: str
    track: list[HurricaneStatus]

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
        AssetTypes.wind_turbines.name :  ProbabilityFunctionBuilder("norm", [0.8, 10]),
        AssetTypes.battery_storage.name : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.transmission_poles.name  :   ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.distribution_poles.name  :  ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.transmission_overhead_lines.name  : ProbabilityFunctionBuilder("lognorm", [0.8, 10, 5]),
        AssetTypes.distribution_overhead_lines.name  :  ProbabilityFunctionBuilder("beta", [0.8, 10, 5]),
    }
    
    def __init__(self,  hurricane_track : LineString , probability_model : dict, hurricane: Hurricane) -> None:
        timestamps = [t.timestamp for t in hurricane.track]
        self.hurricane = hurricane
        super(WindScenario, self).__init__(hurricane_track, probability_model, timestamps)     
        return      
    
    @classmethod
    def from_historical_hurricane_by_sid(cls, hurricane_sid : str, probability_function : dict= None):
        assert os.path.exists(ERAD_DB), f"The data file {ERAD_DB} not found"
        conn = sqlite3.connect(ERAD_DB)
        hurricane_data = pd.read_sql(f"SELECT * FROM {HISTROIC_HURRICANE_TABLE} WHERE `SID ` = '{hurricane_sid}';", conn)
        name = hurricane_data['NAME '][0] 
        hurricane_data = hurricane_data[['LAT (degrees_north)', 'LON (degrees_east)', 'WMO_WIND (kts)', 'WMO_PRES (mb)', 'LANDFALL (km)', 'ISO_TIME ']]
        for col  in ['WMO_WIND (kts)', 'WMO_PRES (mb)', 'LANDFALL (km)']:
            hurricane_data = hurricane_data[hurricane_data[col] != ' ']
        if hurricane_data.empty:
            raise ValueError(f"Hurricane '{hurricane_sid}'  not found in column 'SID', table '{HISTROIC_HURRICANE_TABLE}' in the database")
        conn.close() 
        geometry = [Point(lat, lon) for lat, lon in zip(hurricane_data['LAT (degrees_north)'], hurricane_data['LON (degrees_east)'])]
        cls.hurricane_data = gpd.GeoDataFrame(hurricane_data, geometry=geometry) 
        cls.hurricane_data.set_crs('epsg:4326') 

        track = []
        for idx, row_data in hurricane_data.iterrows():
            track.append(HurricaneStatus(
                timestamp = row_data['ISO_TIME '],
                wind_speed_mph = float(row_data['WMO_WIND (kts)']) * 1.15078,
                pressure_mb = float(row_data['WMO_PRES (mb)']),
                longitude = float(row_data['LON (degrees_east)']),
                latitude = float(row_data['LAT (degrees_north)']),
                landfall_mi= float(row_data['LANDFALL (km)']) * 0.621371
            ))
        hurricane = Hurricane(
            sid = hurricane_sid,
            name = name,
            track = track
        )
        return cls(LineString(geometry), probability_function, hurricane)
        
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
        if hasattr(self, "point"):
            return self.point
        else:
            return Point(self.hurricane.track[0].longitude, self.hurricane.track[0].latitude)
            
    def increment_time(self):
        """Method to increment simulation time for time evolviong scenarios."""
        raise FeatureNotImplementedError()

    def calculate_asset_wind_speed(self, distance_mi: float):
        return distance_mi
        

    def calculate_survival_probability(self, assets : dict) -> dict:
        for asset_type, asset_dict in assets.items():
            assert asset_type in self.probability_model, f"Survival probability for asset type '{asset_type}' not found in the passed probability_model"
            probability_function = self.probability_model[asset_type]
            print("probability_function: ", probability_function, asset_type)
            for asset_name, asset_ppty in asset_dict.items():
                coords = Point(asset_ppty["coordinates"])
                coords = Point(coords.y, coords.x)
                for track in self.hurricane.track:
                    self.point = Point(track.longitude, track.latitude)
                    distance = self.distance_from_centroid(coords)
                    wind_speed = self.calculate_asset_wind_speed(distance)
                    survival_probability = probability_function.probability(wind_speed)
                    
                    if "survival_probability" not in assets[asset_type][asset_name]:
                        assets[asset_type][asset_name]["survival_probability"] = 1
                        assets[asset_type][asset_name]["distance_to_eye"] = []

                    assets[asset_type][asset_name]["survival_probability"] *= survival_probability
                    assets[asset_type][asset_name]["distance_to_eye"].append(distance)  
        return assets
                
    def plot(self):
        self.hurricane_data.plot()
        # plt.show()


