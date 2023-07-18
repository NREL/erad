""" Module for injecting scenario data into graph database. """


from neo4j import GraphDatabase
import shapely

from erad.db import disaster_input_model
from erad.scenarios import earthquake_scenario
from erad.db.assets.distribution_lines import (
    _update_distribution_overhead_lines,
    _update_distribution_underground_lines
)

from erad.db.assets.critical_infras import (
    _update_critical_infra_based_on_grid_access_fast
)


def inject_point_earthquake(
    scenario_input: disaster_input_model.PointEarthquake,
    driver: GraphDatabase.driver,
    critical_infras: None
):
    """Function to update the survival probability of different assets
    due to user input based earthquake scenario.

    Args:
        scenario_input (scenario_model.PointEarthquake): Should be an instance
            of `scenario_model.PointEarthquake` data model.
        driver (GraphDatabase.driver): Instance of `GraphDatabase.driver`
            instance
    """
    if not critical_infras:
        critical_infras = []


    scenario = earthquake_scenario.EarthquakeScenario(
        shapely.geometry.Point(
            scenario_input.longitude, scenario_input.latitude
        ),
        scenario_input.probability_model,
        scenario_input.timestamp,
        Magnitude=scenario_input.magnitude,
        Depth=scenario_input.depth,
    )
    
    _update_distribution_overhead_lines(scenario, driver, scenario_input.timestamp)
    _update_distribution_underground_lines(scenario, driver, scenario_input.timestamp)
    if len(critical_infras):
        _update_critical_infra_based_on_grid_access_fast(critical_infras, driver)
    
            
