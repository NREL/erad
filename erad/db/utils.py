""" This module contains utility functions 
utilized throughout the modules and subpackages
contained within db subpackage."""

from neo4j import GraphDatabase

def _run_read_query(driver:GraphDatabase.driver, cypher_query: str):
    """ Runs a cypher query and returns result. """

    with driver.session() as session:
        result = session.read_transaction(
            lambda tx: tx.run(cypher_query).data()
        )
    return result