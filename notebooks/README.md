### Please use this folder for writing all of your jupyter notebook codes


##### Spinning of Neo4J server using docker container

If don't need to use Graph data science plugin (used in graph traversal algorithms)
use the following command from your terminal (Assuming docker is already installed in your computer)

```
docker run -p 7474:7474 -p 7687:7687 -v C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\neo4j:/data neo4j
```

However if you do need Graph data science plugin use the command below. First you need to download and unzipped the plugin.
Source to download the plugin is https://neo4j.com/graph-data-science-software/ 

```
docker run -p 7474:7474 -p 7687:7687 -v C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\neo4j:/data -v C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\neo4j-graph-data-science-2.1.2:/plugins -e NEO4J_dbms_security_procedures_unrestricted=gds.* -e NEO4J_dbms_security_procedures_whitelist=gds.*  neo4j
```
	