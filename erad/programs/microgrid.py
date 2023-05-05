"""
This module will update the survive proprty based on whether 
the critica infrastructure is going to be powered from microgrid or not.
"""


from neo4j import GraphDatabase

from erad.metrics.check_microgrid import check_for_microgrid


def apply_microgrid_to_critical_infra(
        driver: GraphDatabase.driver,
):
    """ Function that will update the survive property of 
    critical infrastructure if it can get power from microgrid."""

    islands_jsons = check_for_microgrid(driver, output_json_path=None)
    infra_survives = [subdict['sinks'] for _, subdict \
                      in islands_jsons.items() if len(subdict['sources'])>0]

    infra_survives = [x for el in infra_survives for x in el if 'load' not in x]
    
    for infra in infra_survives:
        cypher_query = f"""
                        MATCH (c)
                        WHERE c.name = $cname
                        SET c.survival_probability = 1
                    """

        with driver.session() as session:
                session.write_transaction(
                    lambda tx: tx.run(
                        cypher_query,
                        cname=infra,
                    )
                )