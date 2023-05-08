from shapely.geometry import MultiPolygon, Point,Polygon
from random import random,seed
from enum import IntEnum
import numpy as np

class ScenarioTypes(IntEnum):
    flood_m = 0
    wind_m_per_s = 1
    fire_m = 2
    earthquake_pga = 3
    
class AssetTypes(IntEnum):
    substation = 0
    solar_panels = 1
    buried_lines = 2
    wind_turbines= 3
    battery_storage = 4
    transmission_poles = 5
    distribution_poles = 6
    transmission_overhead_lines = 7
    distribution_overhead_lines = 8
    #substructures
    #conduit_burial

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_
    
    @classmethod
    def has_asset(cls, asset):
        print(asset)
        return asset in cls.__members__


def asset_list(x1=41.255, y1=-117.33, x2=41.255, y2=-117.33, samples=100):

    x = np.linspace(x1, x2, samples)
    y = np.linspace(y1, y2, samples)
    
    seed(3)
    asset_probabilities = {
        AssetTypes.substation: 1 / 10000.0,
        AssetTypes.solar_panels : 1/500,
        AssetTypes.buried_lines : 1/10.0,
        AssetTypes.wind_turbines : 1/5000,
        AssetTypes.battery_storage :1/2000,
        AssetTypes.transmission_poles: 1 / 10.0,
        AssetTypes.distribution_poles : 1 / 10.0,
        AssetTypes.transmission_overhead_lines : 1/10.0,
        AssetTypes.distribution_overhead_lines : 1/10.0,
    }
    
    heights_ft = {
        AssetTypes.substation.name : 3,
        AssetTypes.solar_panels.name : 10,
        AssetTypes.buried_lines.name : -3,
        AssetTypes.wind_turbines.name : 25,
        AssetTypes.battery_storage.name : 4,
        AssetTypes.transmission_poles.name : 0,
        AssetTypes.distribution_poles.name : 0,
        AssetTypes.transmission_overhead_lines.name : 100,
        AssetTypes.distribution_overhead_lines.name : 30,
    }
    
    assets = {
        AssetTypes.substation.name : {},
        AssetTypes.solar_panels.name : {},
        AssetTypes.buried_lines.name : {},
        AssetTypes.wind_turbines.name : {},
        AssetTypes.battery_storage.name :{},
        AssetTypes.transmission_poles.name : {},
        AssetTypes.distribution_poles.name : {},
        AssetTypes.transmission_overhead_lines.name : {},
        AssetTypes.distribution_overhead_lines.name : {},
    }
    
    for asset_type, probability in asset_probabilities.items():
        asset_id = 0
        for x1 in x:
            for y1 in y:    
                if random() < probability:
                    assets[asset_type.name][f"{asset_type.name} {asset_id}"] = {"coordinates" : (x1, y1), "heights_ft": heights_ft[asset_type.name]}
                    asset_id += 1
    
    p1 = Point(x.min(), y.min())
    p2 = Point(x.max(), y.min())
    p3 = Point(x.max(), y.max())
    p4 = Point(x.min(), y.max())
    pointList = [p1, p2, p3, p4, p1]
    poly = Polygon(pointList)
    mypoly = MultiPolygon([poly]) 
    
    return assets, mypoly