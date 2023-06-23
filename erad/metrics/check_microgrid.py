""" This module contains functions and utilities to check for the
possibility of microgrid formation.
"""

from typing import List, Dict
import math
import json

from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt


def create_directed_graph(
    driver: GraphDatabase.driver,
):
    """Creates a directed graph representation of the power network.

    For now we have read all the relationships and nodes. We will need to
    filter this by feeder to avoid running into memory issues in future for
    larger graph.

    Args:
        driver (GraphDatabase.driver): Instance of `GraphDatabase.driver`
            instance
    """

    # Get the buses, customers, pvs, energystorage and line sections
    power_network_query = """
    MATCH (sourceNode:Bus)-[relationship:CONNECTS_TO]-(targetNode:Bus)
    return relationship{.*} , sourceNode {.*}, targetNode{.*}
    """

    # Gettings relations between customers and buses
    customer_bus_network_query = """
    MATCH (sourceNode:Bus)-[relationship:CONSUMES_POWER_FROM]-(targetNode:Load)
    return relationship{.*} , sourceNode {.*}, targetNode{.*}
    """

    # Gettings relations between critical infrastructures and buses
    critical_infra_bus_network_query = """
    MATCH (sourceNode:Bus)-[relationship:GETS_POWER_FROM]-(targetNode)
    return relationship{.*} , sourceNode {.*}, targetNode{.*}
    """

    # Gettting relations between PVs and buses
    pv_bus_network_query = """
    MATCH (sourceNode:Bus)-[relationship:INJECTS_ACTIVE_POWER_TO]-(targetNode:Solar)
    return relationship{.*} , sourceNode {.*}, targetNode{.*}
    """

    # Getting relations between energy storage and buses
    es_bus_network_query = """
    MATCH (sourceNode:Bus)-[relationship:INJECTS_POWER]-(targetNode:EnergyStorage)
    return relationship{.*} , sourceNode {.*}, targetNode{.*}
    """

    relations = []
    for query in [
        power_network_query,
        customer_bus_network_query,
        pv_bus_network_query,
        es_bus_network_query,
        critical_infra_bus_network_query
    ]:

        with driver.session() as session:
            result = session.read_transaction(lambda tx: tx.run(query).data())
        relations.extend(result)

    graph = nx.Graph()
    for rel in relations:

        # Unpack the relationship data
        relationship = rel["relationship"]
        source_node = rel["sourceNode"]
        target_node = rel["targetNode"]

        # Add nodes if not already present in the graph
        for node in [source_node, target_node]:
            if not graph.has_node(node["name"]):
                graph.add_node(node["name"], **node)

        # Add relationship
        graph.add_edge(source_node["name"], target_node["name"], **relationship)

    return graph.to_directed()

def node_connected_to_substation(
    substation_nodes: List[str],
    driver: GraphDatabase.driver
):
    """ Gives list of nodes still connected to substation. """
    directed_graph = create_directed_graph(driver)
    edges_to_be_removed = []

    for edge in directed_graph.edges():
        edge_data = directed_graph.get_edge_data(*edge)
        if "survive" in edge_data and int(edge_data["survive"]) == 0:
            edges_to_be_removed.append(edge)

    if edges_to_be_removed:
        directed_graph.remove_edges_from(edges_to_be_removed)
        wcc = nx.weakly_connected_components(directed_graph)

        for _, weak_component in enumerate(wcc):
            wcc_graph = directed_graph.subgraph(weak_component)
            nodes = wcc_graph.nodes()
            for sub_node in substation_nodes:
                if sub_node in nodes:
                    return nodes
    else:
        nodes = []
        for edge in directed_graph.edges():
            nodes.extend(edge)
        return nodes
    return []
            

def check_for_microgrid(driver: GraphDatabase.driver, output_json_path: str):
    """Checks for possibility of microgrid in each subgraph.

    Args:
        driver (GraphDatabase.driver): Instance of `GraphDatabase.driver`
            instance
       output_json_path (str): JSON file path for exporting the metric.
    """

    directed_graph = create_directed_graph(driver)
    node_data = {item[0]: item[1] for item in directed_graph.nodes(data=True)}

    edges_to_be_removed = []
    subgraphs = {}

    for edge in directed_graph.edges():
        edge_data = directed_graph.get_edge_data(*edge)
        if "survive" in edge_data and int(edge_data["survive"]) == 0:
            edges_to_be_removed.append(edge)

    if edges_to_be_removed:
        directed_graph.remove_edges_from(edges_to_be_removed)
        wcc = nx.weakly_connected_components(directed_graph)

        for id, weak_component in enumerate(wcc):

            # Let's create a networkx representation to perform
            # multiple source multiple sink max flow problem
            # https://faculty.math.illinois.edu/~mlavrov/docs/482-fall-2019/lecture27.pdf
            source_capacity, sink_capacity = 0, 0
            wcc_graph = directed_graph.subgraph(weak_component)
            wcc_graph = nx.DiGraph(wcc_graph)

            for new_node in ["infinity_source", "infinity_sink"]:
                if not wcc_graph.has_node(new_node):
                    wcc_graph.add_node(new_node)

            sinks, sources = [], []
            for node in wcc_graph.nodes():
                # Connect all loads to infinity sink

                if "pv" in node or "es_" in node or node_data.get(node, {}).get('backup', None) == 1:
                    wcc_graph.add_edge(node, "infinity_source", capacity=1e9)
                    wcc_graph.add_edge("infinity_source", node, capacity=1e9)
                    sources.append(node)

                    cap_ = None 
                    if 'kw' in node_data[node]:
                        cap_ = node_data[node]["kw"]
                    elif 'capacity' in node_data[node]:
                        cap_ = node_data[node]["capacity"]
                    elif 'backup_capacity_kw' in node_data[node]:
                        cap_ = node_data[node]["backup_capacity_kw"]
                    else:
                        raise Exception('Not a valid source!')
                    source_capacity += cap_

                elif "load" in node or node_data.get(node, {}).get('survive', None) is not None :
                    wcc_graph.add_edge(node, "infinity_sink", capacity=1e9)
                    wcc_graph.add_edge("infinity_sink", node, capacity=1e9)
                    sinks.append(node)
                    sink_capacity += math.sqrt(
                    node_data[node].get('kW', 0) ** 2
                    + node_data[node].get('kvar', 0) ** 2
                    ) * float(node_data[node].get("critical_load_factor", 0))
                   
            
            # if id == 2:
            #     breakpoint()
            flow_value, _ = nx.maximum_flow(
                wcc_graph, "infinity_source", "infinity_sink", capacity="kva"
            )
    
            subgraphs[f"weak_component_{id}"] = {
                "length": len(weak_component),
                "max_flow": flow_value,
                "sources": sources,
                "sinks": sinks,
                "source_capacity": source_capacity,
                "sink_capacity": sink_capacity,
            }



    if output_json_path:
        with open(output_json_path, "w") as fpointer:
            json.dump(subgraphs, fpointer)

    return subgraphs
