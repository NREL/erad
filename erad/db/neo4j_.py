"""Module contains class and utility functions to manage
interactions with Neo4J database. 
"""

# standard libraries
import os
import logging
from typing import Union


# third-party libraries
from dotenv import load_dotenv
from neo4j import GraphDatabase, basic_auth

# internal imports
from erad.db.credential_model import Neo4jConnectionModel


load_dotenv()
NEO4J_URL = os.getenv("NEO4J_URL")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

logger = logging.getLogger(__name__)


class Neo4J:
    """Class for managing interaction with Neo4J database.

    Attributes:
        neo4j_url (str): URL for connecting to Neo4j
        neo4j_username (str): Username for Neo4j database
        neo4j_password (str): Password for Neo4j database
        use_env (bool): True if above info are to be collected
            from env file.
        driver (GraphDatabase.driver): Neo4J driver instance
    """

    def __init__(
        self,
        neo4j_url: Union[str, None] = None,
        neo4j_username: Union[str, None] = None,
        neo4j_password: Union[str, None] = None,
    ) -> None:
        """Constructor for Neo4J class.

        Args:
            neo4j_url (str): URL for connecting to Neo4j
            neo4j_username (str): Username for Neo4j database
            neo4j_password (str): Password for Neo4j database
        """

        self.neo4j_url = NEO4J_URL if NEO4J_URL else neo4j_url
        self.neo4j_username = (
            NEO4J_USERNAME if NEO4J_USERNAME else neo4j_username
        )
        self.neo4j_password = (
            NEO4J_PASSWORD if NEO4J_PASSWORD else neo4j_password
        )

        connection = Neo4jConnectionModel(
            neo4j_url=self.neo4j_url,
            neo4j_username=self.neo4j_username,
            neo4j_password=self.neo4j_password,
        )

        self.driver = GraphDatabase.driver(
            connection.neo4j_url,
            auth=basic_auth(
                connection.neo4j_username, connection.neo4j_password
            ),
        )

        logger.debug(
            f"Connected to {connection.neo4j_url} database successfully"
        )

    @staticmethod
    def rename_labels(label):
        """Method to replace the invalid character."""
        invalid_chars = ["-", ":", "(", ")", "."]
        for invalid_char in invalid_chars:
            if invalid_char in label:
                label = label.replace(invalid_char, "__")
        return label

    # def add_node(
    #     self,
    #     labels: Union[List, None] = None,
    #     properties: Union[Dict, None] = None,
    # ) -> None:
    #     """Method to add node to the Neo4j database.

    #     Args:
    #         labels (Union[List, None]): List of labels to be used for node
    #         properties (Union[Dict, None]): Properties to be used for the node
    #     """
    #     if labels is None:
    #         labels = []

    #     if properties is None:
    #         properties = {}

    #     labels = ":".join([self.rename_labels(label) for label in labels])
    #     cypher_query = "CREATE (:" + labels + " $properties)"

    #     with self.driver.session() as session:
    #         session.write_transaction(
    #             lambda tx: tx.run(cypher_query, properties=properties)
    #         )

    # def add_relationship(
    #     self,
    #     from_node_label: str,
    #     to_node_label: str,
    #     from_node: str,
    #     to_node: str,
    #     relationship_label: str,
    #     relationship_properties: Union[Dict, None] = None,
    # ) -> None:
    #     """Method to create relationship in graph database.

    #     Args:
    #         from_node_label (str): Node label for from node
    #         to_node_label (str): Node label for to node
    #         from_node (str): From node name
    #         to_node (str): To node name
    #         relationship_label (str): Relationship label name
    #         relationship_properties (Union[Dict, None]): Properties to be used
    #             for relationship
    #     """

    #     if relationship_properties is None:
    #         relationship_properties = {}

    #     cypher_query = (
    #         f"MATCH (a:{from_node_label}),(b:{to_node_label}) WHERE a.name = '{from_node}'"
    #         + f" AND b.name = '{to_node}' CREATE (a)-[:"
    #         + self.rename_labels(relationship_label)
    #         + " $properties]->(b)"
    #     )

    #     with self.driver.session() as session:
    #         session.write_transaction(
    #             lambda tx: tx.run(
    #                 cypher_query, properties=relationship_properties
    #             )
    #         )

    # def read_query(self, cypher_query: str) -> List:
    #     """Executes a Cypher read query."""

    #     with self.driver.session() as session:
    #         result = session.read_transaction(
    #             lambda tx: tx.run(cypher_query).data()
    #         )

    #     return result

    def close_driver(self):
        """Method to close the driver."""
        self.driver.close()
