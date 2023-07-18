""" Module for extracting assets from OpenDSS model.

Examples:

    >>> from erad import utils
    >>> extract_opendss_model(
            <path_to_opendss_master_file>,
            <output_folder>
        )
"""

# standard imports
from genericpath import exists
from pathlib import Path
import logging
from typing import List

# third-party imports
import opendssdirect as dss
import pandas as pd
import networkx as nx
from shapely.geometry import MultiPoint
import stateplane

# internal imports
from erad.utils.util import path_validation, setup_logging
from erad.exceptions import OpenDSSCommandError, MultiStatePlaneError


logger = logging.getLogger(__name__)


def get_transformers(dss_instance: dss) -> List:
    """Function to return list of transformers in opendss models.

    Args:
        dss_instance (dss): OpenDSS instance with models preloaded

    Returns:
        List: List of transformer metadata object
    """

    transformer_container = []
    flag = dss_instance.Transformers.First()
    while flag > 0:
        trans_name = dss_instance.CktElement.Name().lower()
        buses = dss_instance.CktElement.BusNames()
        bus1, bus2 = buses[0].split(".")[0], buses[1].split(".")[0]

        transformer_container.append(
            {
                "name": trans_name,
                "type": "Transformer",
                "source": bus1,
                "target": bus2,
                "kva": dss_instance.Transformers.kVA(),
                "num_phase": dss_instance.CktElement.NumPhases(),
            }
        )
        flag = dss_instance.Transformers.Next()
    return transformer_container


def get_line_sections(dss_instance: dss) -> List:
    """Function to return list of all line segments in opendss model.

    Args:
        dss_instance (dss): OpenDSS instance with models preloaded

    Returns:
        List: List of line segment metadata object
    """
    UNIT_MAPPER = {
        0: 0,
        1: 1.60934,
        2: 0.3048,
        3: 1,
        4: 0.001,
        5: 0.0003048,
        6: 0.0000254,
        7: 0.00001,
    }

    sections_container = []
    flag = dss_instance.Lines.First()
    while flag > 0:
        section_name = dss_instance.CktElement.Name().lower()
        buses = dss_instance.CktElement.BusNames()
        bus1, bus2 = buses[0].split(".")[0], buses[1].split(".")[0]

        sections_container.append(
            {
                "name": section_name,
                "type": "LineSegment",
                "source": bus1,
                "target": bus2,
                "length_km": UNIT_MAPPER[dss_instance.Lines.Units()]
                * dss_instance.Lines.Length(),
                "ampacity": dss_instance.Lines.NormAmps(),
                "num_phase": dss_instance.CktElement.NumPhases(),
            }
        )

        flag = dss_instance.Lines.Next()
    return sections_container


def get_buses(dss_instance: dss) -> List:
    """Function to return list of all buses in opendss model.

    Args:
        dss_instance (dss): OpenDSS instance with models preloaded

    Returns:
        List: List of bus metadata object
    """
    buses_container = []
    for bus in dss_instance.Circuit.AllBusNames():
        dss_instance.Circuit.SetActiveBus(bus)
        buses_container.append(
            {
                "name": bus,
                "type": "Bus",
                "kv": dss_instance.Bus.kVBase(),
                "longitude": dss_instance.Bus.X(),
                "latitude": dss_instance.Bus.Y(),
            }
        )
    return buses_container


def get_capacitors(dss_instance: dss) -> List:
    """Function to return list of all capacitors in opendss model.

    Args:
        dss_instance (dss): OpenDSS instance with models preloaded

    Returns:
        List: List of capacitor metadata object
    """

    capacitors_container = []
    flag = dss_instance.Capacitors.First()
    while flag > 0:
        capacitor_name = dss_instance.CktElement.Name().lower()
        buses = dss_instance.CktElement.BusNames()
        bus1 = buses[0].split(".")[0]

        capacitors_container.append(
            {
                "name": capacitor_name,
                "type": "Capacitor",
                "source": bus1,
                "kv": dss_instance.Capacitors.kV(),
                "kvar": dss_instance.Capacitors.kvar(),
            }
        )

        flag = dss_instance.Capacitors.Next()
    return capacitors_container


def get_pvsystems(dss_instance: dss) -> List:
    """Function to return list of all pv systems in opendss model.

    Args:
        dss_instance (dss): OpenDSS instance with models preloaded

    Returns:
        List: List of PVsystem metadata object
    """

    pvs_container = []
    flag = dss_instance.PVsystems.First()
    while flag > 0:
        pv_name = dss_instance.CktElement.Name().lower()
        buses = dss_instance.CktElement.BusNames()
        bus1 = buses[0].split(".")[0]

        pvs_container.append(
            {
                "name": pv_name,
                "type": "PVSystem",
                "source": bus1,
                "rated_power": dss_instance.PVSystems.Pmpp(),
            }
        )

        flag = dss_instance.PVsystems.Next()
    return pvs_container


def get_loads(dss_instance):
    """Function to return list of all loads in opendss model.

    Args:
        dss_instance (dss): OpenDSS instance with models preloaded

    Returns:
        List: List of load metadata object
    """

    loads_container = []
    flag = dss_instance.Loads.First()
    while flag > 0:
        load_name = dss_instance.CktElement.Name().lower()
        buses = dss_instance.CktElement.BusNames()
        bus1 = buses[0].split(".")[0]

        loads_container.append(
            {
                "name": load_name,
                "type": "Load",
                "source": bus1,
                "kw": dss_instance.Loads.kW(),
                "kvar": dss_instance.Loads.kvar(),
            }
        )

        flag = dss_instance.Loads.Next()
    return loads_container


def execute_dss_command(dss_instance: dss, dss_command: str) -> None:
    """Pass the valid dss command to be executed.

    Args:
        dss_instance (dss): OpenDSS instance with models preloaded
        dss_command (str): DSS command sring to be executed

    Raises:
        OpenDSSCommandError: Raises this because opendss command execution
            ran into error

    """
    error = dss_instance.run_command(dss_command)
    if error:
        logger.error(f"Error executing command {dss_command} >> {error}")
        raise OpenDSSCommandError(
            f"Error executing command {dss_command} >> {error}"
        )
    logger.info(f"Sucessfully executed the command, {dss_command}")


def get_bounding_box(master_file: str, buffer: float = 1000) -> List:
    """Creates a bounding box coordinate for covering region of opendss model.

    Args:
        master_file (str): Path to master dss file
        buffer (float): Buffer distance around distribution model in meter

    Raises:
        MultiStatePlaneError: Raises this if opendss models lies in multiple
            state plane coordinates

    Returns:
        List: List of bounding box coordinates (lower_left, upper_right)
    """

    # Get bounding box for opendss network
    # Do a basic check on the path
    master_file = Path(master_file)
    path_validation(master_file)
    logger.debug(f"Attempting to read case file >> {master_file}")

    # Clear memory and compile dss file
    dss.run_command("Clear")
    dss.Basic.ClearAll()
    execute_dss_command(dss, f"Redirect {master_file}")

    # Get all the points
    points = []
    for bus in dss.Circuit.AllBusNames():
        dss.Circuit.SetActiveBus(bus)
        points.append([dss.Bus.X(), dss.Bus.Y()])

    # Create a multipoint to get bounds
    multi_points = MultiPoint(points)
    bounds = multi_points.bounds

    # Get EPSG value for converting into coordinate reference system
    if stateplane.identify(bounds[0], bounds[1]) != stateplane.identify(
        bounds[2], bounds[3]
    ):
        raise MultiStatePlaneError(
            f"The regions uses multiple stateplane coordinate system"
        )

    epsg_value = stateplane.identify(bounds[0], bounds[1])

    # Let's project all the WGS84 coordinates into
    # transformed coordinates this will make sure distance is in meter
    transformed_points = [
        stateplane.from_lonlat(*point, epsg_value) for point in points
    ]

    # Create a multipoint from the transformed coordinates
    transformed_multipoint = MultiPoint(transformed_points).buffer(buffer)

    # Get the bounds and convert back to wsg84 format
    transformed_bounds = transformed_multipoint.bounds
    bounds_wsg84 = stateplane.to_lonlat(
        transformed_bounds[0], transformed_bounds[1], epsg_value
    ) + stateplane.to_lonlat(
        transformed_bounds[2], transformed_bounds[3], epsg_value
    )

    return bounds_wsg84


def extract_export_opendss_model(
    master_file: str, output_folder_path: str
) -> None:
    """Extract the opendss models and exports into csv file format.

    Args:
        master_file (str): Path to opendss master file
        output_folder_path (str): Folder path for exporting the models to.
    """

    # Do a basic check on the path
    master_file = Path(master_file)
    path_validation(master_file)
    logger.debug(f"Attempting to read case file >> {master_file}")

    # Clear memory and compile dss file
    dss.run_command("Clear")
    dss.Basic.ClearAll()
    execute_dss_command(dss, f"Redirect {master_file}")

    # Initial container
    transformers = get_transformers(dss)
    line_sections = get_line_sections(dss)
    buses = get_buses(dss)
    capacitors = get_capacitors(dss)
    pv_systems = get_pvsystems(dss)
    loads = get_loads(dss)

    output_folder_path = Path(output_folder_path)
    output_folder_path.mkdir(exist_ok=True)
    transformers_df = pd.DataFrame(transformers)
    transformers_df.to_csv(output_folder_path / "transformers.csv")

    line_sections_df = pd.DataFrame(line_sections)
    line_sections_df.to_csv(output_folder_path / "line_sections.csv")

    buses_df = pd.DataFrame(buses)
    buses_df.to_csv(output_folder_path / "buses.csv")

    capacitors_df = pd.DataFrame(capacitors)
    capacitors_df.to_csv(output_folder_path / "capacitors.csv")

    pv_systems_df = pd.DataFrame(pv_systems)
    pv_systems_df.to_csv(output_folder_path / "pv_systems.csv")

    loads_df = pd.DataFrame(loads)
    loads_df.to_csv(output_folder_path / "loads.csv")
