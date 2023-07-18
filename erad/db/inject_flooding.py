""" Module for injecting flooding scenario data into graph database. """


from neo4j import GraphDatabase
from shapely import MultiPolygon, Polygon

from erad.db import disaster_input_model
from erad.scenarios import flood_scenario
from erad.db.assets.distribution_lines import (
    _update_distribution_overhead_lines,
    _update_distribution_underground_lines
)

from erad.db.assets.critical_infras import (
    _update_critical_infra_based_on_grid_access_fast
)


def inject_polygon_flooding(
    scenario_input: disaster_input_model.PolygonFlooding,
    driver: GraphDatabase.driver,
    critical_infras: None
):
    """Function to update the survival probability of different assets
    due to user input based flooding scenario.

    Args:
        scenario_input (scenario_model.PolygonFlooding): Should be an instance
            of `scenario_model.PolygonFlooding` data model.
        driver (GraphDatabase.driver): Instance of `GraphDatabase.driver`
            instance
    """
    if not critical_infras:
        critical_infras = []


    scenario = flood_scenario.FlooadScenario(
        MultiPolygon(
            [Polygon(el) for el in scenario_input.polygon]
        ),
        scenario_input.probability_model,
        scenario_input.timestamp,
        file_flow=scenario_input.file_flow,
        file_levels=scenario_input.file_levels,
        file_gaugues=scenario_input.file_gaugues
    )
    
    _update_distribution_underground_lines(scenario, driver, scenario_input.timestamp)
    _update_distribution_overhead_lines(scenario, driver, scenario_input.timestamp)
    if len(critical_infras):
        _update_critical_infra_based_on_grid_access_fast(critical_infras, driver)
    
            
