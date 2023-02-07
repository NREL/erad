""" Utility functions for dealing with SMART DS dataset. 

Examples:

    >>> from erad import ditto_utils
    >>> ditto_utils.download_smartds_data('P4R',  '.')

"""

# standard libraries
from pathlib import Path
import shutil
import logging
from typing import List

# third-party libraries
import boto3
from botocore import UNSIGNED
from botocore.config import Config
from ditto.store import Store
from ditto.readers.opendss.read import Reader
from ditto.network.network import Network
from ditto.models.power_source import PowerSource
import networkx as nx
from networkx.readwrite import json_graph


# internal libraries
from erad.constants import SMARTDS_VALID_AREAS, SMARTDS_VALID_YEARS
from erad.exceptions import SMARTDSInvalidInput, DittoException
from erad.utils.util import timeit, write_file, path_validation
from erad.utils.util import read_file, setup_logging


logger = logging.getLogger(__name__)


@timeit
def download_aws_dir(
    bucket: str, path: str, target: str, unsigned=True, **kwargs
) -> None:
    """Utility function download data from AWS S3 directory.

    Args:
        bucket (str): Name of the bucket.
        path (str): S3 bucket prefix
        target (str): Path for downloading the data
        unsigned (bool): Indicate whether to use credential or not
        kwargs (dict): Keyword arguments accepted by `boto3.client`
    """

    target = Path(target)
    if unsigned:
        client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    else:
        if kwargs:
            client = boto3.client("s3", **kwargs)
        else:
            client = boto3.client("s3")

    # Handle missing / at end of prefix
    if not path.endswith("/"):
        path += "/"

    paginator = client.get_paginator("list_objects_v2")
    for result in paginator.paginate(Bucket=bucket, Prefix=path):

        # Download each file individually
        for key in result["Contents"]:

            # Calculate relative path
            rel_path = key["Key"][len(path) :]

            # Skip paths ending in /
            if not key["Key"].endswith("/"):
                local_file_path = target / rel_path
                local_file_path.parent.mkdir(parents=True, exist_ok=True)
                client.download_file(bucket, key["Key"], str(local_file_path))


@timeit
def download_smartds_data(
    smartds_region: str,
    output_path: str = "./smart_ds_downloads",
    year: int = 2018,
    area: str = "SFO",
    s3_bucket_name: str = "oedi-data-lake",
    folder_name: str = "opendss_no_loadshapes",
    cache_folder: str = "cache",
) -> str:
    """Utility function to download SMARTDS data from AWS S3 bucket.

    Args:
        smartds_region (str): SMARTDS region name
        output_path (str): Path for downloaded data
        year (int): Valid year input for downloading the data
        area (str): Valid SMARTDS area
        s3_bucket_name (str): S3 bucket name storing the SMARTDS data
        folder_name (str): S3 bucket folder to download
        cache_folder (str): Folder path for caching the results

    Raises:
        SMARTDSInvalidInput: Raises this error if year and/or area
            provided is not valid.

    Returns:
        str: Folder path containing downloaded data.
    """
    if year not in SMARTDS_VALID_YEARS or area not in SMARTDS_VALID_AREAS:
        raise SMARTDSInvalidInput(
            f"Not valid input! year= {year} area={area}, \
            valid_years={SMARTDS_VALID_YEARS}, valid_areas={SMARTDS_VALID_AREAS}"
        )

    output_path = Path(output_path)
    cache_folder = Path(cache_folder)

    output_path.mkdir(exist_ok=True)
    cache_folder.mkdir(exist_ok=True)

    cache_key = (
        f"{smartds_region}__{year}__{area}__{s3_bucket_name}_{folder_name}"
    )
    cache_data_folder = cache_folder / cache_key
    output_folder = output_path / cache_key

    if cache_data_folder.exists():
        logger.info(f"Cache hit for {cache_data_folder}")
        shutil.copytree(cache_data_folder, output_folder, dirs_exist_ok=True)

    else:
        logger.info(
            f"Cache missed reaching to AWS for downloading the data ..."
        )
        output_folder.mkdir(exist_ok=True)
        prefix = f"SMART-DS/v1.0/{year}/{area}/{smartds_region}/scenarios/base_timeseries/{folder_name}/"
        download_aws_dir(s3_bucket_name, prefix, output_folder)
        shutil.copytree(output_folder, cache_data_folder, dirs_exist_ok=False)

    logger.info(f"Check the folder {output_folder} for downloaded data")
    return output_folder


@timeit
def _create_networkx_from_ditto(
    output_path: str, file_name: str, **kwargs
) -> List:
    """Creates networkx graph from OpenDSS model using Ditto.

    Args:
        output_path (str): Path to store the networkx
            data in json file format
        file_name (str): JSON file name used to export
            the network
        kwargs (dict): Keyword arguments accepted
            by Ditto

    Raises:
        DittoException: Raises if multiple sources are found.


    Returns:
        List: Pair of networkx graph and
            path containing JSON file
    """
    file_name = Path(file_name).stem
    logger.debug(
        "Attempting to create NetworkX representation from OpenDSS \
        files using DiTTo"
    )

    path_validation(output_path)

    store = Store()
    reader = Reader(
        master_file=kwargs["master_file"],
        buscoordinates_file=kwargs["buscoordinates_file"],
        coordinates_delimiter=kwargs["coordinates_delimiter"],
    )
    reader.parse(store)

    all_sources = []
    for i in store.models:
        if isinstance(i, PowerSource) and i.connecting_element is not None:
            all_sources.append(i)
        elif isinstance(i, PowerSource):
            print(
                "Warning - a PowerSource element has a None connecting element"
            )

    if len(all_sources) > 1:
        raise DittoException(
            f"This feeder has lots of sources {len(all_sources)}"
        )

    ditto_graph = Network()
    ditto_graph.build(store, all_sources[0].connecting_element)
    ditto_graph.set_attributes(store)

    data = dict(ditto_graph.graph.nodes.data())
    data_new = {}
    for node, node_data in data.items():
        try:
            data_new[node] = node_data["positions"][0]._trait_values
        except Exception as e:
            connecting_node = node_data["connecting_element"]
            data_new[node] = data[connecting_node]["positions"][0]._trait_values

    adj_file = file_name + ".adjlist"
    nx.write_adjlist(ditto_graph.graph, output_path / adj_file)
    g = nx.read_adjlist(output_path / adj_file)
    nx.set_node_attributes(g, data_new)

    data = json_graph.adjacency_data(g)
    json_file = file_name + ".json"
    output_file = output_path / json_file
    write_file(data, output_file)

    logger.debug(
        f"Successfully created json file representing the network \
        check the file {output_file}"
    )

    return (g, output_file)


def create_networkx_from_ditto(
    output_path: str, file_name: str, **kwargs
) -> None:
    """Creates networkx graph from OpenDSS model using Ditto.

    Args:
        output_path (str): Path to store the networkx
            data in json file format
        file_name (str): JSON file name used to export
            the network
        kwargs (dict): Keyword arguments accepted
            by Ditto
    """
    try:
        output_path = Path(output_path)
        return _create_networkx_from_ditto(output_path, file_name, **kwargs)
    finally:
        for file_path in output_path.iterdir():
            if file_path.suffix == ".adjlist":
                file_path.unlink(missing_ok=True)


def create_networkx_from_json(json_file_path: str):
    """Returns networkx graph from JSON file."""
    content = read_file(json_file_path)
    return json_graph.adjacency_graph(content)
