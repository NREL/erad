""" Modules for testing utility functions. """
from pathlib import Path
import shutil

from erad.utils import ditto_utils


def test_smartds_feeder_download():
    """Test function for downloading SMART DS feeders from AWS."""

    ditto_utils.download_smartds_data("P35U", ".")
    folder_path = Path("P35U__2018__SFO__oedi-data-lake_opendss_no_loadshapes")
    assert folder_path.exists()
    shutil.rmtree(folder_path)
