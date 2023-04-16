# from .logging_config import get_console_handler
import logging
import pathlib
from sys import exit

from raman_fitting import __package_name__

logger = logging.getLogger(__name__)


# import pandas as pd
# pd.options.display.max_rows = 10
# pd.options.display.max_columns = 10
# __package_name__ = 'raman_fitting'

CONFIG_FILE = pathlib.Path(__file__).resolve()
PACKAGE_ROOT = CONFIG_FILE.parent.parent
MODEL_DIR = PACKAGE_ROOT / "deconvolution_models"

# TESTS_ROOT_DIR = PACKAGE_ROOT.parent.parent / "tests"
# TESTS_ROOT_DIR =
TESTS_DATASET_DIR = PACKAGE_ROOT / "datafiles" / "example_files"

# Home dir from pathlib.Path for storing the results
PACKAGE_HOME = (
    pathlib.Path.home() / f".{__package_name__}"
)  # pyramdeconv is the new version package name


try:
    if not PACKAGE_HOME.is_dir():
        try:
            logger.warning(
                f"Package home directory did not exist, will now be created at:\n{PACKAGE_HOME}\n--------------------"
            )
            PACKAGE_HOME.mkdir()
        except Exception as exc:
            logger.warning(
                f"Package home mkdir unexpected error\n{exc}.\nFolder{PACKAGE_HOME} could not be created, exiting."
            )
            exit()
    else:
        logger.info(
            f"Package home directory exists at:\n{PACKAGE_HOME}\n--------------------"
        )
except Exception as exc:
    logger.warning(
        f"Unexpected error with checking for package home folder:\nFolder:{PACKAGE_HOME}\nError:\n{exc}\n {__package_name__} can not run."
    )
    exit()


TESTS_RESULTS_DIR = PACKAGE_HOME / "test_results"

DATASET_DIR = PACKAGE_HOME / "datafiles"
RESULTS_DIR = PACKAGE_HOME / "results"

# Optional local configuration file
LOCAL_CONFIG_FILE = PACKAGE_HOME / "local_config.py"

# Storage file of the index
INDEX_FILE_NAME = f"{__package_name__}_index.csv"
