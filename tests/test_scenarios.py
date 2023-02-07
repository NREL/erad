from erad.scenarios.earthquake_scenario import EarthquakeScenario
from erad.scenarios.fire_scenario import FireScenario
from erad.scenarios.utilities import ProbabilityFunctionBuilder
import numpy as np


def create_samples():
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
    return assets, survival_model


def test_fire_scenario():
    assets, survival_model = create_samples()
    Fire1 = FireScenario.from_historical_fire_by_code("GHP4", survival_model)
    assets = Fire1.calculate_survival_probability(assets, False) # True for a plot

    
def test_earthquake_scenario():
    assets, survival_model = create_samples()
    earthquake_1 = EarthquakeScenario.from_historical_earthquake_by_code("USP000GYZK", None)
    assets = earthquake_1.calculate_survival_probability(assets)
