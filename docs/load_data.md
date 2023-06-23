
First step in using ERAD is preparing the dataset to load into the database.
This section describes data format and the process for loading datasets into database.

## Distribution Feeder Data

One of the key dataset for simulation is distribution feeder data. You need to prepare csv files for distribution assets which will be used to bulk load the data into Neo4J database using Cypher Query. Here is a list of csv files you need to prepare for distribution system. You can also use the sample datasets [available in the repository](https://github.com/NREL/erad/tree/main/tests/data/csvs_for_graph).


<!-- {{ read_csv('../tests/data/csvs_for_graph/buses.csv') }} -->


| File Name | Description | Columns |
| -----------| ----------- |  |
| `buses.csv` | CSV file containing information about distribution system buses. Required. | `name`, `longitude`, `latitude`  |
| `loads.csv` | CSV file containing information about power system loads. Required. `source` refer to bus name from `buses.csv` file where load is connected to and `critical_load_factor` is any value between 0 and 1 that is used to determine critical demand for this load. | `name`, `kw`, `kvar`, `source`, `critical_load_factor` | 
| `transformers.csv` | CSV file containing information about transformers. Required. `source` and `target` refer to bus names from `buses.csv` file where transformer's primary and secondary terminal is connected to. `height_m` is height of transformer from ground surface in meters. | `name`, `source`, `target`, `kva`, `height_m`|
| `line_sections.csv` | CSV file containing information about line sections. Required. `source` and `target` refer to bus names from `buses.csv` file where line segment's to and from node is connected to. `height_m` is height of line segment from ground surface in meters and `geom_type` could be either `overhead` or `underground`. | `name`, `source`, `target`, `geom_type`, `ampacity`, `height_m`|
| `pv_systems.csv`| CSV file containing information about PV systems. Optional. `owner` refers to load name from `load.csv` file who owns the solar, `bus` refers to bus name from `buses.csv` file where solar is connected to and `capacity` refers to solar installation capacity in kW. | `name`, `owner`, `bus`, `capacity`|
| `energy_storage.csv` | CSV file containing information about energy storages. Optional. `owner` refers to load name from `load.csv` file who owns the energy storage, `bus` refers to bus name from `buses.csv` file where energy storage is connected to, `kwh` refers to energy capacity for storage, `kw` refers to maximum kw capacity for storage, and `soc` refers to initial state of charge for the storage. |`name`, `owner`, `bus`, `soc`, `kwh`, `kw` |
| `substation.csv` | CSV file containing information about distribution substation. Required. | `name` |


If you are using OpenDSS models, ERAD includes utility functions to extract required csv files from the model.

Following code snippet downloads one of the SMARTDS feeder dataset and extracts asset data in csv file format in `assets` folder.

```python
from erad.utils.ditto_utils import download_smartds_data
from erad.utils.opendss_utils import extract_export_opendss_model

download_smartds_data('P3R', '.')
extract_export_opendss_model('P3R__2018__SFO__oedi-data-lake_opendss_no_loadshapes/Master.dss',
                              './assets')
```

You will see `buses.csv`, `capacitors.csv`, `line_sections.csv`, `load.csv`, `pv_systems.csv`, and `transformers.csv`. Notice that the extraction process can generate extra files not used by ERAD and may extract more information than you need and this is okay as long as csv files have all the necessary columns you will be okay.


## Critical Infrastructure Data

Along with distribution feeder data, ERAD also requires critical infrastructure data. Here is a list of csv files you need to prepare for critical infrastructures. You do not need to have all the dataset and can start with any subset of these.

| File Name | Description | Columns |
| -----------| ----------- | ---  |
| `medical_centers.csv` | CSV file containing information about medicial centers within the region of interest. Optional. | `gid`, `name`, `source`, `longitude`, `latitude`, `backup` |
| `shelters.csv` | CSV file containing information about shelters. Optional. | `gid`, `name`, `source`, `longitude`, `latitude`, `backup`|
| `pharmacies.csv` | CSV file containing information about pharmacies within the region of interest. Optional. | `gid`, `name`, `source`, `longitude`, `latitude`, `backup` |
| `groceries.csv` | CSV file containing information about groceries within the region of interest. Optional.  | `gid`, `name`, `source`, `longitude`, `latitude`, `backup` |
| `banking.csv` | CSV file containing information about banks within the region of interest. Optional. | `gid`, `name`, `source`, `longitude`, `latitude`, `backup` |
| `convenience.csv` | CSV file containing information about convenience stores within the region of interest. Optional. | `gid`, `name`, `source`, `longitude`, `latitude`, `backup` |

`gid` refers to any unique global identifier, `source` is bus name from `buses.csv` file where it is connected to distribution grid, `name` is a friendly name for infrastructure and `backup` is binary 0 or 1.

One of the dataset you can use to get critical infrastructure data is [HIFLD dataset](https://hifld-geoplatform.opendata.arcgis.com/).