# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2022-8-11

# Updated

- Renamed package name from src to erad
- Renamed subpackage storing neo4j_ module to be db
- Renamed storage subpackage to visulaization
- Rename hifld module to hifld_utils module
- Added docstrings for modules in subpackages db, utils, visualization and root level modules constants.py and exceptions.py

## [Unreleased] - 2022-7-13


# Added
    
- Added bulk_load_cypher_queries.txt file including sample queries to load CSV data to neo4j database
## [Unreleased] - 2022-7-7


# Added
    
- Added hifld module to process the HIFLD CSV data set to create
      subset of the data based on feeder region and create relationship
      between load and critical infrastructure
- Added opendss_utils module to parse generic opendss file and create
      csv metadata

# Updated

- Updated neo4j_ module to add generic relationship
- Updated the name of utils module to be util module to remove import
      conflict
- Updated README to add instructions for installation as well as ways to
      generate CSV files

## [Unreleased] - 2022-6-28

# Added

- Added sample Cypher queries
- Added package called plots and added module called graph.py to basicnetworkx type graph visualization
- Added scenario package to manage the resilience scenarios
# Updated

- Updated logging.yaml file to include logs from new modules
- Updated REDAME.md within notebook bolder
- Updated requirements.txt file
- Updated neo4j_ module to add relationships
- 
## [Unreleased] - 2022-06-15

### Added
    - Added ditto_utils module in utils package
    - Added ability to download SMARTDS data from AWS S3 
    - Added constants module at the root level to manage constants
    - Added exception class to handle input error while downloading SMART DS data
  
## [Unreleased] - 2022-06-14

### Added
    - Added storage package and neo4j module inside
    - Added feature for connecting to neo4j database and ability to add node data in the database ( This may not be used just exploring)
    - Added concrete classes on top of abstract base NetowrkXComaptibleFile and NetworkFromGeoJSON(incomplete)
    - Added .env file for handling secrets and environment variables
    - Added exception class to handle wrong file type, empty environment variable and missing database connection info

### Updated
    - Updated path_validation utility function to check for file type is specified
    - Updated abstractGraph class to include feature to write graph into a file (JSON, AjacencyList, EdgeList)

### Removed


## [Unreleased] - 2022-06-13

### Added
    - Added utils package and utils module inside the utils package
    - Added exceptions module at src folder level to handle exceptions
    - Added utility functions to write and read JSON, YAML and GeoJSON files in utils module
    - Added utility function to setup logging 
    - Added sample logging.yaml file at the src level
    - Added base exception class along with exceptions for handling path issue and feature not implemented issue

### Changed

### Removed

## [0.0.0] - 2022-05-31
### Added
    - Added skeleton for python project
