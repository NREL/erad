""" Module for testing microgrid formation."""
import networkx as nx

from erad.metrics import check_microgrid
from erad.db import neo4j_


def test_create_directed_graph():
    """Function for testing creation of directed graph."""

    neo4j_instance = neo4j_.Neo4J()
    graph = check_microgrid.create_directed_graph(neo4j_instance.driver)
    neo4j_instance.close_driver()
    assert isinstance(graph, nx.Graph)


def test_check_for_microgrid():
    """Function for testing possibility of microgrid formation."""

    neo4j_instance = neo4j_.Neo4J()
    subgraphs = check_microgrid.check_for_microgrid(
        neo4j_instance.driver, "./microgrid.json"
    )
    neo4j_instance.close_driver()
