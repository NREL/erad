""" This module will update the backup property for 
critical infrastructure. """

# standard imports
from typing import List
import random

# third party imports
from neo4j import GraphDatabase

# internal imports
from erad.db.utils import _run_read_query

def apply_backup_program(
    driver: GraphDatabase.driver,
    electricity_backup: any,
    critical_infras: List[str],
):

    """ Function that will update the backup 
    property of critical infras based on backup percentage.
    
    Args:
        driver (GraphDatabase.driver): Neo4J Driver instance
        electricity_backup (float): backup percentage number between 0 and 1 or list of infras to set as backup
        critical_infras (List[str]): list of critical infrastructure
    """

    infra_with_backups = []
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
                SET c.backup = $backup
            """

            if not isinstance(electricity_backup, list):
                backup = 1 if random.random() < electricity_backup else 0
            else:
                backup = 1 if infra['c.name'] in electricity_backup else 0 

            if backup == 1:
                infra_with_backups.append(infra['c.name'])

            with driver.session() as session:
                session.write_transaction(
                    lambda tx: tx.run(
                        cypher_write_query,
                        cname=infra['c.name'],
                        backup= backup
                    )
                )

    return infra_with_backups