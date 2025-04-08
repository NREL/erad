Let's see how you can compute metrics. You can compute these metrics post disaster. Click here to learn more about [disaster modeling](earthquake_modeling.md) in ERAD.

## Computing energy resilience score

Use this snippet to compute energy resilience score. 

```python
from erad.metrics import metric
from erad.db import neo4j_

neo4j_instance = neo4j_.Neo4J(
                neo4j_url='bolt://localhost:7687',
                neo4j_username='neo4j', 
                neo4j_password='neo4j')

metric.energy_resilience_by_customer(
    neo4j_instance.driver, "./energy_resilience.csv",
    critical_infras=["Grocery", "Hospital","Convenience", "Shelter", "Banking"] 
    )

```

## Checking if customer is connected to grid

```python
from erad.metrics import metric
from erad.db import neo4j_

neo4j_instance = neo4j_.Neo4J(
                neo4j_url='bolt://localhost:7687',
                neo4j_username='neo4j', 
                neo4j_password='neo4j')

metric.is_customer_getting_power(
        neo4j_instance.driver, "./is_customer_connected.csv")
```