""" Utility functions that can be used in various parts of the code. """

# standard libraries
import json
from pathlib import Path
import logging
import logging.config
import time
from typing import Union

# third-party libraries
import yaml
import geojson

# internal imports
from erad.exceptions import (
    FeatureNotImplementedError,
    PathDoesNotExist,
    NotAFileError,
    InvalidFileTypePassed,
)

logger = logging.getLogger(__name__)


def timeit(func):
    """Decorator for timing execution of a function."""

    def wrapper(*args, **kwargs):
        time_start = time.perf_counter()
        logger.debug(f"Timing for {func} started")
        ret_val = func(*args, **kwargs)
        time_elapsed = time.perf_counter() - time_start
        # memory_mb =resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0/1024.0
        logger.debug(
            f"Time took to execute the function {func} \
            with args {args}, kwargs {kwargs} is {time_elapsed} seconds"
        )
        return ret_val

    return wrapper


def setup_logging(filename: Union[str, None] = None) -> None:
    """Creates log directory and sets up logging via logging.yaml.

    Args:
        filename (str): Path to logging.yaml file

    If not providex expects log file in the root of repo.
    """

    if filename is None:
        filename = Path(__file__).parents[2] / "logging.yaml"

    logging.config.dictConfig(read_file(filename))


def path_validation(
    file_path: str,
    check_for_file: bool = False,
    check_for_file_type: Union[str, None] = None,
) -> None:
    """Utility function for validating the path.

    Args:
        file_path (str): Path to be validated
        check_for_file (bool): Checks for existence of file
        check_for_file_type (Union[str, None]): Check if file is of
            this type

    Raises:
        PathDoesNotExist: Raises if path does not exist
        NotAFileError: Raises if file is not present
        InvalidFileTypePassed: Raises if invalid file type is passed
    """

    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"{file_path} does not exist!")
        raise PathDoesNotExist(file_path)

    if check_for_file and file_path.is_dir():
        logger.error(f"Expected file but got folder : {file_path} ")
        raise NotAFileError(file_path)

    if check_for_file_type and file_path.suffix != check_for_file_type:
        raise InvalidFileTypePassed(file_path, check_for_file_type)

    logger.debug(f"{file_path} validated successfully!")


@timeit
def read_file(file_path: str) -> dict:
    """Utility function to read file into a python dict.

    Supports json, yaml and geojson.

    Args:
        file_path (str): Path to a file to be read.

    Raises:
        FeatureNotImplementedError: Raises if invalid file is passed.

    Returns:
        dict: Python dict containing content of file.
    """

    file_path = Path(file_path)
    logger.debug(f"Attempting to read {file_path}")

    path_validation(file_path, check_for_file=True)

    # Handle JSON file read
    if file_path.suffix == ".json":
        with open(file_path, "r") as f:
            content = json.load(f)

    # Handle YAML file read
    elif file_path.suffix == ".yaml":
        with open(file_path, "r") as f:
            content = yaml.safe_load(f)

    # Handle geojson file read
    elif file_path.suffix == ".geojson":
        with open(file_path, "r") as f:
            content = geojson.load(f)

    else:
        logger.error(
            f"Could not read the {file_path}, this feature is not yet implemented"
        )
        raise FeatureNotImplementedError(
            f"File of type {file_path.suffix} \
            is not yet implemented for reading purpose"
        )

    logger.debug(f"{file_path} read successfully")
    return content


def write_file(content: dict, file_path: str, **kwargs) -> None:
    """Utility function to write to a file..

    Supports json, yaml and geojson.

    Args:
        content (dict): Python dict content
        file_path (str): Path to a file to be read
        kwargs (dict): Keyword arguments passed to
            relevant writer.

    Raises:
        FeatureNotImplementedError: Raises if invalid file type is passed.
    """
    file_path = Path(file_path)
    path_validation(file_path.parent)

    # Handle JSON file write
    if file_path.suffix == ".json":
        with open(file_path, "w") as f:
            json.dump(content, f, **kwargs)

    # Handle YAML file write
    elif file_path.suffix == ".yaml":
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f, **kwargs)

    # Handle geojson file write
    elif file_path.suffix == ".geojson":
        with open(file_path, "w") as f:
            geojson.dump(content, f, **kwargs)

    else:
        raise FeatureNotImplementedError(
            f"File of type {file_path.suffix} \
            is not yet implemented for writing purpose"
        )
