""" Module for injecting scenario data into graph database. """

import random
from typing import List

from neo4j import GraphDatabase
import shapely

from erad.db import scenario_model
from erad.scenarios import earthquake_scenario


def inject_point_earthquake(
    scenario_input: scenario_model.PointEarthquake,
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

    # Get overhead assets
    cypher_query = """
                    MATCH (b1:Bus)-[r:CONNECTS_TO]-(b2:Bus)
                    WHERE r.ampacity IS NOT NULL
                    RETURN r.longitude, r.latitude, r.name
                """
    with driver.session() as session:
        result = session.read_transaction(
            lambda tx: tx.run(cypher_query).data()
        )

    # Get Groceries
    critical_infras_items = {}
    for infra in critical_infras:
        cypher_query = f"""
                        MATCH (c:{infra})
                        RETURN c.longitude, c.latitude, c.name
                    """
        with driver.session() as session:
            critical_infras_items[infra] = session.read_transaction(
                lambda tx: tx.run(cypher_query).data()
            )

    assets = {
        "overhead_power_lines": {
            line["r.name"]: {
                "coordinates": [line["r.longitude"], line["r.latitude"]]
            }
            for line in result
            if all([line["r.longitude"], line["r.latitude"]])
        }
    }

    for c_infra, data in critical_infras_items.items():
        assets[c_infra] =  {
            item["c.name"]: {
                "coordinates": [item["c.longitude"], item["c.latitude"]]
            } for item in data
            if all([item["c.longitude"], item["c.latitude"]])
        }

    survival_prob = scenario.calculate_survival_probability(assets)

    # update the survival probability
    cypher_query = """
                    MATCH (b1:Bus)-[r:CONNECTS_TO {name: $rname}]-(b2:Bus)
                    SET r.survive = $survive
                    SET r.survival_probability = $s_prob
                """

    with driver.session() as session:
        for rname, rdict in survival_prob["overhead_power_lines"].items():
            session.write_transaction(
                lambda tx: tx.run(
                    cypher_query,
                    rname=rname,
                    s_prob=rdict["survival_probability"],
                    survive=int(
                        random.random() < rdict["survival_probability"]
                    ),
                )
            )
    
    # update the survival probability
    for infra in critical_infras:
        cypher_query = f"""
                        MATCH (c:{infra})
                        WHERE c.name = $cname
                        SET c.survive = $survive
                        SET c.survival_probability = $s_prob
                    """

        with driver.session() as session:
            for cname, cdict in survival_prob[infra].items():
                session.write_transaction(
                    lambda tx: tx.run(
                        cypher_query,
                        cname=cname,
                        s_prob=cdict["survival_probability"],
                        survive=int(
                            random.random() < cdict["survival_probability"]
                        ),
                    )
                )
            
