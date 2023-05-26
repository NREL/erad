""" Module for handling computation of equity and resilience metrics.

Idea is to create separate function for computing each metric. 
"""

from pathlib import Path
from typing import Callable, Union, Dict, List
import json

from neo4j import GraphDatabase
import pandas as pd
import numpy as np

from erad.utils import util
from erad import exceptions


def validate_export_path(file_path: Union[str, Path], file_type: str):
    """Function for validating the export file path.

    Args:
        file_path (Union[str, Path]): Export file path
        file_type (str): File type to be exported e.g. .csv
    """

    output_path = Path(file_path)
    util.path_validation(output_path.parent)
    if output_path.suffix != file_type:
        raise exceptions.InvalidFileTypePassed(output_path, file_type)


def is_customer_getting_power(
    driver: GraphDatabase.driver, output_csv_path: str,
    load_list: List[str] = None
):

    """Function for checking whether customer is still connected
    to substation or not.

    Args:
        driver (GraphDatabase.driver): Instance of `GraphDatabase.driver`
            instance
        output_csv_path (str): CSV file path for exporting the metric.
    """
    if not load_list:
        load_list = []

    validate_export_path(output_csv_path, ".csv")
    cypher_query = """
                    MATCH (b:Bus)
                    MATCH (s:Substation)
                    WHERE b <> s
                    WITH b, shortestPath((b)-[:CONNECTS_TO*]-(s)) as p
                    MATCH (c:Load)-[:CONSUMES_POWER_FROM]-(b)
                    WITH c, p, apoc.coll.min([r in relationships(p) | r.survive]) AS max_p
                    RETURN c.name, max_p
                """
    metric_container = {"load_name": [], "metric": []}
    with driver.session() as session:
        result = session.read_transaction(
            lambda tx: tx.run(cypher_query).data()
        )

        for item in result:
            metric_container["load_name"].append(item["c.name"])
            metric_container["metric"].append(item["max_p"] \
                                              if item["c.name"] not in load_list else 1)

    df = pd.DataFrame(metric_container)
    df.to_csv(output_csv_path)


def energy_resilience_by_customer(
    driver: GraphDatabase.driver, output_csv_path: str,
    critical_infras: List = ["Grocery", "Hospital", "Pharmacy"]
):
    """Function for checking whether customer is still connected
    to substation or not.

    Args:
        driver (GraphDatabase.driver): Instance of `GraphDatabase.driver`
            instance
        output_csv_path (str): CSV file path for exporting the metric.
    """

    validate_export_path(output_csv_path, ".csv")

    metric_container = {"load_name": [], "metric": [], "critical_service": []}
    with driver.session() as session:

        for cs in critical_infras:
            cypher_query = (
                f"""
                    MATCH (lo:Load)
                    MATCH (cs:{cs})
                    """
                + """
                    WITH lo,cs, 
                        point.distance(point({longitude: lo.longitude, latitude:lo.latitude}), 
                        point({longitude: cs.longitude, latitude:cs.latitude}))/1000 AS d
                    RETURN lo.name, sum(toInteger(toBoolean(cs.survive) OR toBoolean(cs.backup))/d) AS gamma
                    """
                    # count(d)/sum(d) AS gamma
                    # WHERE cs.survive = 1 
            )
            result = session.read_transaction(
                lambda tx: tx.run(cypher_query).data()
            )

            for item in result:
                metric_container["load_name"].append(item["lo.name"])
                metric_container["metric"].append(item["gamma"])
                metric_container["critical_service"].append(cs)

    df = pd.DataFrame(metric_container)
    df.to_csv(output_csv_path)


def equity_based_energy_resilience_by_income(
    driver: GraphDatabase.driver,
    path_to_energy_resilience_metric: str,
    output_json_path: str,
    category: Dict[str, Callable] = {
        "low": lambda x: x < 90000,
        "medium": lambda x: (90000 < x < 110000),
        "high": lambda x: x > 110000,
    },
):
    """Function to compute the equity based energy resilience metric.

    Args:
        driver (GraphDatabase.driver): Instance of `GraphDatabase.driver`
            instance
        path_to_energy_resilience_metric (str): Path to energy resilience metric.
        output_json_path (str): JSON file path for exporting the metric.
        category (Dict[str, Callable]): Income categories
    """

    validate_export_path(output_json_path, ".json")
    util.path_validation(path_to_energy_resilience_metric)

    metric_container = {}

    with driver.session() as session:

        cypher_query = """
                            MATCH (lo:Load)
                            RETURN lo.income as income, lo.name as name
                        """
        result = session.read_transaction(
            lambda tx: tx.run(cypher_query).data()
        )

    resilience_metric = pd.read_csv(path_to_energy_resilience_metric)
    gamma_dict = (
        resilience_metric.groupby("load_name").sum()["metric"].to_dict()
    )

    for id, func in category.items():

        metric, income_flag_sum = 0, 0
        for load in result:
            load_income_flag = func(load["income"])
            metric += load_income_flag * gamma_dict[load["name"]]
            income_flag_sum += load_income_flag

        metric_container[id] = (
            metric / income_flag_sum if income_flag_sum else None
        )

    metric_values = [val for _, val in metric_container.items() if val]
    if metric_values:
        metric_container["community_resilience_equity_score"] = np.mean(
            metric_values
        ) / np.std(metric_values)

    with open(output_json_path, "w") as fpointer:
        json.dump(metric_container, fpointer)
