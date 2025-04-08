import time

from erad.scenarios.flood_scenario import DynamicFloodInterface, FloodScenario
from erad.scenarios.common import asset_list


def test_dymanic_flood_interface():
    assets, multiploygon = asset_list(38.46, -122.95, 38.53, -122.80)
    flood_1 = FloodScenario.from_live_data(multiploygon, None, None, None, None )
    timestamp = flood_1.valid_timepoints[10]
    assets = flood_1.calculate_survival_probability(assets, timestamp)

def test_flood_interface():
    assets, multiploygon = asset_list(38.46, -122.95, 38.53, -122.80)
    flood_1 = FloodScenario.from_historical_flood_by_code()

    # scatter_points = flood_1.get_gauge_locations()
    # x, y, z, w = flood_1.map_elevation(flood_1.valid_timepoints[0])
    # interface = DynamicFloodInterface(x, y, z, flood_1.levels)

    # for timestamp in flood_1.valid_timepoints:
    #     x, y, z, w = flood_1.map_elevation(timestamp)
    #     interface.update(scatter_points, w, timestamp)
    #     time.sleep(0.1)
    #     break
