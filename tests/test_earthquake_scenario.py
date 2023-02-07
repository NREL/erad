""" Module for testing earthquake resilience scenario. """

import datetime
import shapely

from erad.scenarios import earthquake_scenario
from erad.db import inject_scenario
from erad.db import scenario_model
from erad.db import neo4j_


def test_injecting_earthquake_scenario():

    scenario_input = scenario_model.PointEarthquake(
        longitude=-121.72125955960196, 
        latitude=37.92770173811863,
        probability_model={},
        timestamp=datetime.datetime(2022, 1, 1, 0, 0, 0),
        magnitude=8.0,
        depth=30.0,
    )
    neo4j_instance = neo4j_.Neo4J()

    inject_scenario.inject_point_earthquake(
        scenario_input, neo4j_instance.driver
    )
    neo4j_instance.close_driver()


def test_earthquake_sceanario_from_point():

    center = shapely.geometry.Point(10, 20)
    probability_model = {}
    scenario = earthquake_scenario.EarthquakeScenario(
        center,
        probability_model,
        datetime.datetime.now(),
        Magnitude=6.5,
        Depth=30.0,
    )

    survical_prob = scenario.calculate_survival_probability(
        {
            "overhead_power_lines": {
                "asset_1": {"coordinates": (10.000123, 20.00034)}
            }
        }
    )
    # {'overhead_power_lines': {'asset_1': {'coordinates': (10.000123, 20.00034),
    # 'survival_probability': 0.9761921321820812}}}
    assert isinstance(survical_prob, dict)
