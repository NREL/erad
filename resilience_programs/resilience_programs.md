
## Microgrid program

When disaster event knocks out distribution assets such as lines, poles, transformers etc,  multiple islands gets formed. Microgrid program analyzes each island and figures out whether enough generating resources are available to fulfill electricity demand and designates island as microgrid or not. If island is designated as microgrid all the critical infrastructures connected to the same island that did not survive post disaster is going to be updated as survived for further metric computation. Here is a code snippet to apply microgrid program.

```python

from erad.metrics import metric
from erad.db import neo4j_
from erad.programs.microgrid import apply_microgrid_to_critical_infra

# make sure to update url, username and password for 
# neo4j database
neo4j_instance = neo4j_.Neo4J(
                neo4j_url='bolt://localhost:7687',
                neo4j_username='neo4j', 
                neo4j_password='neo4j')

apply_microgrid_to_critical_infra(neo4j_instance.driver)
```

You can recompute the metrics after applying microgrid program as shown in
[here](./computing_metrics.md).

## Electrcity Backup program for Critical Infrastrcuture

You can choose the percentage of critical infrastrcutures to have electricty backup.
The backup capacity for each infrastructure must have been defined during data pre loading process. This algorithm only selects infrastructures to activate the backup. Once backup is activated, the infrastructure is considered "survived" even if it is not getting power from the distribution grid assuming it can meet it's electricity demand from the backup.
Here is a code snippet to apply electricity backup program for critical infrastructures.

```python

from erad.metrics import metric
from erad.db import neo4j_
from erad.programs.backup import apply_backup_program

# make sure to update url, username and password for 
# neo4j database
neo4j_instance = neo4j_.Neo4J(
                neo4j_url='bolt://localhost:7687',
                neo4j_username='neo4j', 
                neo4j_password='neo4j')

apply_backup_program(neo4j_instance.driver)
```

You can recompute the metrics after applying microgrid program as shown in
[here](./computing_metrics.md).