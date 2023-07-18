""" This module contains functions to update 
survival probability and survive property
based on disaster event. """

# manage python imports
from datetime import datetime 
import random

from neo4j import GraphDatabase

from erad.db.utils import _run_read_query
from erad.metrics.check_microgrid import node_connected_to_substation


def _update_critical_infra_based_on_grid_access_fast(
    critical_infras,
    driver: GraphDatabase.driver   
):
    """ A faster function to update survive attribute 
    based on whether critical infra has access to grid power."""
    # Let's get substation 
    cypher_query = f"""
        MATCH (n:Substation)
        WHERE n.survive is NULL OR n.survive<>0 
        RETURN n.name
    """
    substations = _run_read_query(driver, cypher_query)
    substations = [item["n.name"]  for item in substations]
    
    nodes = node_connected_to_substation(substations, driver)

    # Get all critical infra and check if they are in above nodes
    for cri_infra in critical_infras:
        cypher_query = f"""
                        MATCH (c:{cri_infra})
                        RETURN c.longitude, c.latitude, c.name, c.backup
                    """
        infras = _run_read_query(driver, cypher_query)
        
        for infra in infras:
            
            cypher_write_query = f"""
                MATCH (c:{cri_infra})
                WHERE c.name = $cname
                SET c.survive = $survive
                SET c.survival_probability = $s_prob
            """

            with driver.session() as session:
                session.write_transaction(
                    lambda tx: tx.run(
                        cypher_write_query,
                        cname=infra['c.name'],
                        s_prob= 1 if infra['c.name'] in nodes or int(infra['c.backup'])==1 else 0,
                        survive=1 if infra['c.name'] in nodes or int(infra['c.backup'])==1 else 0 
                    )
                )



def _update_critical_infra_based_on_grid_access(
    critical_infras,
    driver: GraphDatabase.driver 
):
    """ A function to update survive attribute 
    based on whether critical infra has access to grid power."""

    # Let's get substation 
    cypher_query = f"""
        MATCH (n:Substation)
        WHERE n.survive is NULL OR n.survive<>0 
        RETURN n.name
    """
    substations = _run_read_query(driver, cypher_query)
    substations = [item["n.name"]  for item in substations]

    for cri_infra in critical_infras:
        cypher_query = f"""
                        MATCH (c:{cri_infra})
                        RETURN c.longitude, c.latitude, c.name, c.backup
                    """
        infras = _run_read_query(driver, cypher_query)
        
        for infra in infras:
            connected = []
            for substation in substations:

                _name = "{name:" + f'"{infra["c.name"]}"' + "}"
                substation_name = "{name:" + f'"{substation}"' + "}"
                cypher_query = f"""
                    MATCH 
                        (g:{cri_infra} {_name})-[:GETS_POWER_FROM]-(b:Bus),
                        (s:Substation {substation_name}),
                        p=shortestPath((b)-[:CONNECTED_TO*]-(s))
                    WHERE all(r in relationships(p) WHERE r.survive is NULL OR r.survive<>0 )
                    RETURN length(p)
                """

                if not infra['c.backup']: 
                    path = _run_read_query(driver, cypher_query)
                    connected.append(1 if path else 0) 
                else:
                    connected.append(1)
                

            cypher_write_query = f"""
                MATCH (c:{cri_infra})
                WHERE c.name = $cname
                SET c.survive = $survive
                SET c.survival_probability = $s_prob
            """

            with driver.session() as session:
                session.write_transaction(
                    lambda tx: tx.run(
                        cypher_write_query,
                        cname=infra['c.name'],
                        s_prob= int(any(connected)),
                        survive=int(any(connected)) 
                    )
                )

def _update_critical_infra(
        scenario,
        critical_infras,
        driver: GraphDatabase.driver,
        timestamp: datetime 
):

    critical_infras_items = {}
    assets = {}

    for infra in critical_infras:
        cypher_query = f"""
                        MATCH (c:{infra})
                        RETURN c.longitude, c.latitude, c.name
                    """
        critical_infras_items[infra] = _run_read_query(driver, cypher_query)

    
    for c_infra, data in critical_infras_items.items():
        assets[c_infra] =  {
            item["c.name"]: {
                "coordinates": [item["c.longitude"], item["c.latitude"]]
            } for item in data
            if all([item["c.longitude"], item["c.latitude"]])
        }

    survival_prob = scenario.calculate_survival_probability(assets, datetime.now())
    
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