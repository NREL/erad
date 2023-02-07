""" Module for testing the metric computation."""

from pathlib import Path

from erad.metrics import metric
from erad.db import neo4j_


def test_is_customer_getting_power():
    """Function for testing whether customer is still getting
    power or not."""

    neo4j_instance = neo4j_.Neo4J()
    metric.is_customer_getting_power(
        neo4j_instance.driver, "./is_customer_connected.csv"
    )
    neo4j_instance.close_driver()


def test_energy_resilience_by_customer():
    """Function for testing `energy_resilience_by_customer` metric."""

    neo4j_instance = neo4j_.Neo4J()
    metric.energy_resilience_by_customer(
        neo4j_instance.driver, "./energy_resilience.csv"
    )
    neo4j_instance.close_driver()


def test_equity_based_energy_resilience_by_income():
    """Test function to compute the equity resilience by customer."""

    energy_resilience_metric_path = (
        Path(__file__).parent / "data" / "metric_data" / "energy_resilience.csv"
    )
    neo4j_instance = neo4j_.Neo4J()
    metric.equity_based_energy_resilience_by_income(
        neo4j_instance.driver,
        energy_resilience_metric_path,
        "./equity_based_energy_resilience_metric.json",
    )
    neo4j_instance.close_driver()
