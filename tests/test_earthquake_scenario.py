""" Module for testing earthquake resilience scenario. """

import datetime
import shapely

from erad.scenarios.earthquake_scenario import EarthquakeScenario
from erad.scenarios.common import asset_list
from erad.db import neo4j_


# def test_injecting_earthquake_scenario():

#     scenario_input = disaster_input_model.PointEarthquake(
#         longitude=-121.72125955960196, 
#         latitude=37.92770173811863,
#         probability_model={},
#         timestamp=datetime.datetime(2022, 1, 1, 0, 0, 0),
#         magnitude=8.0,
#         depth=30.0,
#     )
#     neo4j_instance = neo4j_.Neo4J()

#     inject_earthquake.inject_point_earthquake(
#         scenario_input, neo4j_instance.driver
#     )
#     neo4j_instance.close_driver()


def test_earthquake_sceanario_from_point():

    center = shapely.geometry.Point(10, 20)
    probability_model = None
    scenario = EarthquakeScenario(
        center,
        probability_model,
        datetime.datetime.now(),
        Magnitude=6.5,
        Depth=30.0,
    )

    survical_prob = scenario.calculate_survival_probability(
        {
            "distribution_overhead_lines": {
                "asset_1": {"coordinates": (10.000123, 20.00034)}
            },
        },
        datetime.datetime.now(),
    )
    
    assert isinstance(survical_prob, dict)
    assert 'survival_probability' in survical_prob['distribution_overhead_lines']['asset_1']
    assert isinstance(survical_prob['distribution_overhead_lines']['asset_1']['survival_probability'], float)

def test_earthquake_scenario():
    assets, _ = asset_list()
    earthquake_1 = EarthquakeScenario.from_historical_earthquake_by_code("USP000GYZK")
    assets = earthquake_1.calculate_survival_probability(assets, None)

def test_earthquake_plot():
    earthquake_1 = EarthquakeScenario.from_historical_earthquake_by_code("USP000GYZK")
    earthquake_1.plot(10)