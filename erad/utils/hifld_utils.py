""" Module for parsing Homeland infrastructure foundation level-data.

Idea is to take the bounding box and find the subset of 
infrastructure in that region.
"""
# standard imports
from pathlib import Path
import math
from typing import Union, List

# third-party imports
import pandas as pd
import stateplane

# internal imports
from erad.utils.util import path_validation


def get_subset_of_hifld_data(
    csv_file: str,
    bounds: List,
    output_folder: str,
    logitude_column_name: str = "X",
    latitude_column_name: str = "Y",
    columns_to_keep: List[str] = ["X", "Y"],
    name_of_csv_file: Union[str, None] = None,
) -> None:
    """Extracts a subset of HIFLD data set.

    Args:
        csv_file (str): Path to HIFLD data csv file
        bounds (List): Bounding box coordinates
        output_folder (str): Path to output folder
        logitude_column_name (str): Expects column with name 'X'
        latitude_column_name (str): Expects column with name 'Y'
        columns_to_keep (List): List of column names to keep
            by default keeps all of them
       name_of_csv_file (Union[str, None]): Name of csv file to export
            filtered set
    """

    # Unpacking the bounds data
    longitude_min, latitude_min, longitude_max, latitude_max = bounds

    # Do a path validation
    csv_file = Path(csv_file)
    output_folder = Path(output_folder)
    path_validation(csv_file, check_for_file=True, check_for_file_type=".csv")
    path_validation(output_folder)

    # Reading the hifld csv data
    df = pd.read_csv(csv_file)

    # filtering for bounds
    df_filtered = df[
        (df[logitude_column_name] >= longitude_min)
        & (df[logitude_column_name] <= longitude_max)
        & (df[latitude_column_name] >= latitude_min)
        & (df[latitude_column_name] <= latitude_max)
    ]

    # Keep only the limited columns
    df_subset = df_filtered[columns_to_keep]

    # export the subset
    file_name = name_of_csv_file if name_of_csv_file else csv_file.name
    df_subset.to_csv(output_folder / file_name)


def get_relationship_between_hifld_infrastructures(
    hifld_data_csv: str,
    unique_id_column: str,
    load_csv: str,
    bus_csv: str,
    output_csv_path: str,
    distance_threshold: float = 2000.0,
):
    """Creates a relationship between consumers and HIFLD infrastructures.

    Args:
        hifld_data_csv (str): Path to filtered HIFLD data csv file
        unique_id_column (List): Column name used as identifier
            for critical infrastructures
        load_csv (str): Path to load csv file
        bus_csv (str): Path to bus csv file
        output_csv_path (str): output csv path for storing relationship csv
        distance_threshold (float): Distance threshold used for mapping
            customer to critical infrastructure
    """
    hifld_data_csv = Path(hifld_data_csv)
    bus_csv = Path(bus_csv)
    load_csv = Path(load_csv)
    output_csv_path = Path(output_csv_path)

    path_validation(
        hifld_data_csv, check_for_file=True, check_for_file_type=".csv"
    )
    path_validation(bus_csv, check_for_file=True, check_for_file_type=".csv")
    path_validation(load_csv, check_for_file=True, check_for_file_type=".csv")
    path_validation(output_csv_path.parents[0])

    hifld_data_df = pd.read_csv(hifld_data_csv)
    load_df = pd.read_csv(load_csv)
    bus_df = pd.read_csv(bus_csv)

    merged_data = pd.merge(
        load_df, bus_df, how="left", left_on="source", right_on="name"
    ).to_dict(orient="records")

    # Container for storing shelter relationships
    _relationship = []
    for _record in hifld_data_df.to_dict(orient="records"):
        _lon, _lat = _record["LONGITUDE"], _record["LATITUDE"]

        # convert into state plane coordinates
        _lon_translated, _lat_translated = stateplane.from_lonlat(_lon, _lat)

        # Loop through all the loads
        for load_record in merged_data:

            load_lon, load_lat = (
                load_record["longitude"],
                load_record["latitude"],
            )

            # convert into state plane coordinates
            load_lon_translated, load_lat_translated = stateplane.from_lonlat(
                load_lon, load_lat
            )

            # computes distance
            distance = math.sqrt(
                (_lat_translated - load_lat_translated) ** 2
                + (_lon_translated - load_lon_translated) ** 2
            )

            if distance < distance_threshold:
                _relationship.append(
                    {
                        unique_id_column: _record[unique_id_column],
                        "load_name": load_record["name_x"],
                        "distance": distance,
                    }
                )

    df = pd.DataFrame(_relationship)
    df.to_csv(output_csv_path)
