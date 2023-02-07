""" Module for managing exceptions raised by ERAD package."""

# standard libraries
from pathlib import Path


class ERADBaseException(Exception):
    """All exception should derive from this."""


class FeatureNotImplementedError(ERADBaseException):
    """Exception raised because specific feature requested has not been implemented."""


class PathDoesNotExist(ERADBaseException):
    """Exception raised bacause expected file/folder path does not exist."""

    def __init__(self, path):
        self.message = (
            f"Expected path {path} does not exist. please check you file path!"
        )
        super().__init__(self.message)


class NotAFileError(ERADBaseException):
    """Exception raised because file is expected but folder path is provided."""

    def __init__(self, path):
        self.message = f"Expected file path {path} is not a file!"
        super().__init__(self.message)


class EmptyEnvironmentVariable(ERADBaseException):
    """Exception raised because environment variable required is empty."""


class DatabaseMissingInfo(ERADBaseException):
    """Exception raised because information required to connect to database is missing."""


class InvalidFileTypePassed(ERADBaseException):
    """Exceptions raised because invalid file type is passed."""

    def __init__(self, path, valid_type):

        self.message = f"Invalid file type of {Path(path).suffix} is passed! Please pass valid file type of {valid_type}"
        super().__init__(self.message)


class SMARTDSInvalidInput(ERADBaseException):
    """Exceptions raised because invalid input is provided for SMART DS data download."""


class EmptyScenarioPolygon(ERADBaseException):
    """Exceptions raised because no polygons are found."""


class OpenDSSCommandError(ERADBaseException):
    """Exceptions raised because opendss command execution ran into an error."""


class MultiStatePlaneError(ERADBaseException):
    """Exceptions raised because the corrdinates are in more than one state plane
    coordinates."""


class DittoException(ERADBaseException):
    """Exceptions raised because application ran into an issus using Ditto."""
