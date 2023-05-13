""" This module contains a function to get the distribution 
line assets and update it's survival probability and survive
attribute based on event scenario. 
"""

# Manage python imports
from datetime import datetime
import random
import json
import random

random.seed(20)

from neo4j import GraphDatabase

from erad.db.utils import _run_read_query


def _create_assets(lines):
    """ Takes the list of lines and convert into
    asset dictionary. """

    return {
            line["r.name"]: {
                "coordinates": [line["r.latitude"], line["r.longitude"]],
                "heights_ft": float(line["r.height_m"])*3.28084,
                "elevation_ft": random.randint(50, 400)
            }
            for line in lines
            if all([line["r.longitude"], line["r.latitude"]])
        }

def _update_distribution_lines_survival(
    survival_probability,
    driver: GraphDatabase.driver   
):
    """ Takes survival probabilty and update survival 
    probability and survive property. """

  

    cypher_query = """
                    MATCH (b1:Bus)-[r:CONNECTS_TO {name: $rname}]-(b2:Bus)
                    SET r.survive = $survive
                    SET r.survival_probability = $s_prob
                """
    with driver.session() as session:
        for rname, rdict in survival_probability.items():
            session.write_transaction(
                lambda tx: tx.run(
                    cypher_query,
                    rname=rname,
                    s_prob=rdict.get("survival_probability", 1),
                    survive=int(random.random() < rdict.get("survival_probability", 1)),
                )
            )


def _update_distribution_overhead_lines(scenario, driver: GraphDatabase.driver, timestamp: datetime):
    """Get overhead lines and update the survival probability."""

    # Cypher query to get overhead line segments
    cypher_query = """ 
                    MATCH (b1:Bus)-[r:CONNECTS_TO]-(b2:Bus)
                    WHERE r.ampacity IS NOT NULL AND r.type = 'overhead'
                    RETURN r.longitude, r.latitude, r.name, r.type, r.height_m
                """
    overhead_lines = _run_read_query(driver, cypher_query)

    if overhead_lines:
        assets = {"distribution_overhead_lines": _create_assets(overhead_lines)}

        survival_prob = scenario.calculate_survival_probability(assets, timestamp)

        # with open('surv.json', "w") as fp:
        #     json.dump(survival_prob,fp)
        _update_distribution_lines_survival(
            survival_prob['distribution_overhead_lines'],
            driver
        )

def _update_distribution_underground_lines(scenario, driver: GraphDatabase.driver, timestamp: datetime):
    """Get overhead lines and update the survival probability."""

    # Cypher query to get overhead line segments
    cypher_query = """ 
                    MATCH (b1:Bus)-[r:CONNECTS_TO]-(b2:Bus)
                    WHERE r.ampacity IS NOT NULL AND r.type = 'underground'
                    RETURN r.longitude, r.latitude, r.name, r.type, r.height_m
                """
    underground_lines = _run_read_query(driver, cypher_query)

    if underground_lines:
        assets = {"buried_lines": _create_assets(underground_lines)}

        survival_prob = scenario.calculate_survival_probability(assets, timestamp)
        _update_distribution_lines_survival(
            survival_prob['buried_lines'],
            driver
        )

