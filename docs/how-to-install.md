
## Package Installation

We recommend using Anaconda or Miniconda to create the environment and instal ERAD. 
Use the commands below to create environment and install the ERAD python package.

=== ":fontawesome-brands-windows: Windows 10"

    ``` cmd
    conda create -n erad python==3.8
    conda activate erad
    conda install shapely
    pip install NREL-erad==1.0.0
    ```

=== ":fontawesome-brands-apple: + :fontawesome-brands-linux: Mac OS & linux"

    ``` cmd
    conda create -n erad python==3.8
    conda activate erad
    pip install NREL-erad==1.0.0
    ```

## Neo4J Installation

ERAD uses neo4j database for storing underlying asset data and performing computation. First step in using ERAD is to install neo4J. You can either install neo4J Desktop (You can download latest neo4J version [here](https://neo4j.com/download/). ) or use docker to start up 
neo4j container. You can use following command to start up a neo4j docker container. We recommend using docker to setup neo4j. [Use this documentation](https://docs.docker.com/engine/install/) to install docker if you have not already installed it in your machine.

```docker
docker run -d \
    -p 7474:7474 -p 7687:7687 \
    --env NEO4J_dbms_memory_transaction_total_max=10g \
    --env NEO4J_server_memory_heap_max__size=10g \
    -v /data:/data \
    -v /plugins:/plugins \
    -v /import:/import \
    --name neo4j-apoc \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4JLABS_PLUGINS=\[\"apoc\"\] \
    neo4j:5.7.0-community
```

Notice volume mount for import (`-v /import:/import`). You would need to copy all the csv files (described in [Loading data into database](load_data.md) section.) before running cypher queries. You can keep the `plugins` and `data` folder empty. Make sure to update host paths for volume mount correctly before running above command. Also if your machine does not have more than 20 GB worth of RAM reduce both heap size and dbms transaction memory settings. Feel free to tune those as per your requirements.

If you are using neo4J desktop, you will need to create new database and install `apoc` library for that database which you can do by navigating neo4J Desktop UI. Feel free to edit the setting file to upgrade memory if you are working with bigger dataset. You would need to find out depending on where you installed neo4J desktop, appropriate folder for dumping csv files as for each database neo4J creates a new folder with unique UUID. The trick I use is to run cypher query to load random csv file (Learn more about loading data using Cypher query in [Loading data into database](load_data.md) section.) in neo4j browser and looking at path in error string.


