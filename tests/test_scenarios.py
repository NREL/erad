
from erad.scenarios.earthquake_scenario import EarthquakeScenario
from erad.scenarios.utilities import ProbabilityFunctionBuilder
from erad.scenarios.common import AssetTypes, ScenarioTypes
from erad.scenarios.flood_scenario import FlooadScenario
from erad.scenarios.fire_scenario import FireScenario
from erad.scenarios.wind_scenario import WindScenario
from shapely.geometry import MultiPolygon, Point,Polygon
from erad.scenarios.common import asset_list
from scipy.spatial import ConvexHull
from random import random, seed
import numpy as np



def test_fire_scenario():
    assets, _ = asset_list()
    Fire1 = FireScenario.from_historical_fire_by_code("GHP4")
    assets = Fire1.calculate_survival_probability(assets, None, False)
    #Fire1.plot()

    
def test_earthquake_scenario():
    assets, _ = asset_list()
    earthquake_1 = EarthquakeScenario.from_historical_earthquake_by_code("USP000GYZK")
    assets = earthquake_1.calculate_survival_probability(assets)

def test_flood_scenario():

    assets, multiploygon = asset_list(38.46, -122.95, 38.53, -122.80)
    flood_1 = FlooadScenario.from_live_data(multiploygon, None, None, None, None )
    timestamp = flood_1.valid_timepoints[-1]
    assets = flood_1.calculate_survival_probability(assets, timestamp)
    print(assets)
    

def test_wind_scenario():
    assets = asset_list()
    wind_1 = FlooadScenario.from_historical_earthquake_by_code("USP000GYZK")
    assets = wind_1.calculate_survival_probability(assets, None, None, None, None)

