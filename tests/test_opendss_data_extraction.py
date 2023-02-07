""" This module includes tests for extracting csv data from opendss models. """
from pathlib import Path
import shutil

from erad.utils import opendss_utils
from erad.utils import hifld_utils
from erad.utils import opendss_utils


def test_extract_csv_from_opendss():
    """Test function for extracting data from opendss model."""

    master_file = (
        Path(__file__).parent
        / "data"
        / "test_opendss_model_p35u"
        / "Master.dss"
    )
    opendss_utils.extract_export_opendss_model(master_file, "csv_extracts")
    shutil.rmtree("./csv_extracts")


def test_get_medical_centers():
    """Test function for getting critical infrastructure data."""

    master_file = (
        Path(__file__).parent
        / "data"
        / "test_opendss_model_p35u"
        / "Master.dss"
    )
    bounds = opendss_utils.get_bounding_box(master_file, 5000)

    medical_centre_hifld_data = (
        Path(__file__).parent
        / "data"
        / "critical_infras"
        / "sample_emergency_medical_centers.csv"
    )
    hifld_utils.get_subset_of_hifld_data(
        medical_centre_hifld_data,
        bounds,
        ".",
        logitude_column_name="LONGITUDE",
        latitude_column_name="LATITUDE",
        columns_to_keep=[
            "LONGITUDE",
            "LATITUDE",
            "STATE",
            "ZIP",
            "CITY",
            "COUNTY",
        ],
        name_of_csv_file="medical_centers.csv",
    )

    Path("medical_centers.csv").unlink()
