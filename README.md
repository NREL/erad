# erad
Graph based python tool for computing equitable resilience 

[Visit full documentation here](https://github.nrel.gov/pages/ERAD/erad/)

### :rocket: Installation

1. Create a virtual environment using Anaconda

```
    conda create -n erad python==3.9
```

After creating the environment activate the environment

```
 conda activate erad
```

2. If you are on windows install these pakages first. Otherwise proceed to step 3.

```
    conda install shapely
    conda install geopandas
```

3. Install the package using the command below

```
    pip install -e.
```
### :point_right: Generating CSV data set to load to Graph database

1. Downloading the SMARTDS opendss feeder model
   
Use the following code snippet to download the OpenDSS model for the region
you are interested in. Just provide the region name and where you would like the downloaded files to be stored.

```
from utils.ditto_utils import download_smartds_data
download_smartds_data('P4R',  r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\smartds_opendss_models')
```

2. Parsing generic opendss model to retrieve metadata

The command below takes master opendss file and folder where you want to store the extracted data. It will generate csvs for distribution assets.

```
from utils.opendss_utils import extract_opendss_model
extract_opendss_model(
        r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\smartds_opendss_models\P4R__2018__SFO__oedi-data-lake_opendss_no_loadshapes\Master.dss',
        r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\graph_csvs'
    )
```

3. Preparing HIFLD data for the region you are interested in

First download the HIFLD CSV data set and use the following command to get the subset of the csv for the region you are interedted in. First create a bounding box with 5km buffer. Then use the bounding box corners to filter the csv data set.

```
from utils.opendss_utils import get_bounding_box
from utils.hifld import get_subset_of_hifld_data
bounds = get_bounding_box(
    r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\smartds_opendss_models\P4R__2018__SFO__oedi-data-lake_opendss_no_loadshapes\Master.dss', 
    5000)

get_subset_of_hifld_data(
    r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\HIFLD Data\Emergency_Medical_Service_(EMS)_Stations.csv',
    bounds,
    r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\graph_csvs',
    logitude_column_name='LONGITUDE',
    latitude_column_name='LATITUDE',
    columns_to_keep=['LONGITUDE', 'LATITUDE', 
    'STATE', 'ZIP', 'CITY', 'COUNTY'],
    name_of_csv_file='medical_centers.csv')
```

4. Creating relationship between HIFLD data and OpenDSS loads

Use the following snippet to create a relationship csv between HIFLD data and OpenDSS loads

```
from utils.hifld import get_relationship_between_hifld_infrastructures
get_relationship_between_hifld_infrastructures(
        r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\graph_csvs\medical_centers.csv',
        'Id',
        r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\graph_csvs\loads.csv',
        r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\graph_csvs\buses.csv',
        r'C:\Users\KDUWADI\Desktop\NREL_Projects\RADS\graph_csvs\medical_relationships.csv'
    )
```