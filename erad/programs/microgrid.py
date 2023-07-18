"""
This module will update the survive property based on whether 
the critica infrastructure is going to be powered from microgrid or not.
"""


from neo4j import GraphDatabase

from erad.metrics.check_microgrid import check_for_microgrid


def apply_microgrid_to_critical_infra(
        driver: GraphDatabase.driver,
        factor: float= (0.5 * 0.4)
):
    """ Function that will update the survive property of 
    critical infrastructure if it can get power from microgrid."""

    islands_jsons = check_for_microgrid(driver, output_json_path=None)
    infra_island = [subdict['sinks'] for _, subdict \
                      in islands_jsons.items() if len(subdict['sources'])>0]
    infra_microgrid = [1 if subdict['source_capacity'] >= subdict['sink_capacity']*factor  else 0 for _, subdict \
                      in islands_jsons.items()]

    infra_survives = [el for id, el in enumerate(infra_island) \
                      if infra_microgrid[id]]
    all_sinks = [x for el in infra_survives for x in el]
    infra_survives = [x for el in infra_survives for x in el if 'load' not in x]
    
    for infra in infra_survives:
        cypher_query = f"""
                        MATCH (c)
                        WHERE c.name = $cname
                        SET c.survive = 1
                        SET c.survival_probability = 1
                    """

        with driver.session() as session:
                session.write_transaction(
                    lambda tx: tx.run(
                        cypher_query,
                        cname=infra,
                    )
                )
    return all_sinks