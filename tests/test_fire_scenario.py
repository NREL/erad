from erad.scenarios.fire_scenario import FireScenario
from erad.scenarios.common import asset_list


from uuid import UUID

def test_fire_scenario_from_name():
    assets, _ = asset_list()
    Fire1 = FireScenario.from_historical_fire_by_name("Horse Pasture")
    assets = Fire1.calculate_survival_probability(assets, None, False)
    

def test_fire_scenario_from_uuid():
    assets, _ = asset_list()
    Fire1 = FireScenario.from_historical_fire_by_uuid('{A183D683-4BAA-494B-9A99-700915935D1A}')
    assets = Fire1.calculate_survival_probability(assets, None, False)
    
def test_fire_scenario_plot():
    assets, _ = asset_list()
    Fire1 = FireScenario.from_historical_fire_by_name("Horse Pasture")
    Fire1.plot()