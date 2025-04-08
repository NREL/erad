### <u>Downloading the SMARTDS opendss feeder model</u>
   
Use the following code snippet to download the OpenDSS model for the region
you are interested in. Just provide the region name and where you would like the downloaded files to be stored.

``` python
from utils.ditto_utils import download_smartds_data
download_smartds_data('P4R',  r'./smartds_opendss_models')
```

### <u>Parsing generic opendss model to retrieve metadata</u>

The command below takes master opendss file and folder where you want to store the extracted data. It will generate csvs for distribution assets.

```python
from utils.opendss_utils import extract_opendss_model
extract_opendss_model(
        r'smartds_opendss_models\P4R__2018__SFO__oedi-data-lake_opendss_no_loadshapes\Master.dss',
        r'./graph_csvs'
    )
```

### <u>Preparing HIFLD data for the region of interest </u>

First download the HIFLD CSV data set and use the following command to get the subset of the csv for the region you are interedted in. First create a bounding box with 5km buffer. Then use the bounding box corners to filter the csv data set.

```python
from utils.opendss_utils import get_bounding_box
from utils.hifld import get_subset_of_hifld_data
bounds = get_bounding_box(
    r'smartds_opendss_models\P4R__2018__SFO__oedi-data-lake_opendss_no_loadshapes\Master.dss', 
    5000)

get_subset_of_hifld_data(
    r'./Emergency_Medical_Service_(EMS)_Stations.csv',
    bounds,
    r'./graph_csvs',
    logitude_column_name='LONGITUDE',
    latitude_column_name='LATITUDE',
    columns_to_keep=['LONGITUDE', 'LATITUDE', 
    'STATE', 'ZIP', 'CITY', 'COUNTY'],
    name_of_csv_file='medical_centers.csv')
```
