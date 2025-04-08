from erad.scenarios.wind_scenario import WindScenario
from erad.scenarios.common import asset_list
from pprint import pprint as print

def test_hurricane_scenario():
    assets, _ = asset_list()
    hurricane_1 = WindScenario.from_historical_hurricane_by_sid("1980001S13173")
    assets = hurricane_1.calculate_survival_probability(assets)
    print(assets)
