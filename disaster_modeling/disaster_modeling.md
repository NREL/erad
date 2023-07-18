
Currently you can model earthquake, flooding and fire in ERAD. Fire model is still under development and documentation is not included for fire for now.

## Simulating earthquake

The snippets below shows an example for simulating earthquake in ERAD. 

```python
import datetime 

from erad.db import neo4j_
from erad.db import inject_earthquake
from erad.db import disaster_input_model

# Make sure to update the url, username and password
neo4j_instance = neo4j_.Neo4J(
                neo4j_url='bolt://localhost:7687',
                neo4j_username='neo4j', 
                neo4j_password='neo4j')


earthquake = disaster_input_model.PointEarthquake(
            longitude=-121.72125955960196, 
            latitude=37.92770173811863,
            timestamp=datetime.datetime(2022, 1, 1, 0, 0,0),
            magnitude=6.0,
            depth=15.0
        )

inject_earthquake.inject_point_earthquake(
        earthquake, neo4j_instance.driver,
        critical_infras=["Grocery", "Hospital","Convenience", "Shelter", "Banking"])
```
We first created a neo4j database instance by passing neo4j host url, username and password. Secondly we defined input model for point earthquake by passing relevant input parameters. Lastly `inject_point_earthquake` takes the input, database driver and list of critical infrastructure which need to be updated following the simulation.

