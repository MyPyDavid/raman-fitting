# from .logging_config import get_console_handler
import logging
import pathlib

from .. import __package_name__

logger = logging.getLogger(__package_name__)

# import pandas as pd
# pd.options.display.max_rows = 10
# pd.options.display.max_columns = 10

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

TESTS_RESULTS_DIR = PACKAGE_HOME / "test_results"

DATASET_DIR = PACKAGE_HOME / "datafiles"
RESULTS_DIR = PACKAGE_HOME / "results"
# Storage file of the index
INDEX_FILE_NAME = f"{__package_name__}_index.csv"
INDEX_FILE = RESULTS_DIR / INDEX_FILE_NAME
# Optional local configuration file
LOCAL_CONFIG_FILE = PACKAGE_HOME / "local_config.py"


# ADAPT to your own configurations
if LOCAL_CONFIG_FILE.is_file():
    try:
        # PACKAGE_ROOT, MODEL_DIR are not locally configurated
        from .local_config import DATASET_DIR, INDEX_FILE, RESULTS_DIR

        print(
            f" Importing settings from local config...",
            "\n",
            f"RESULTS_DIR : {RESULTS_DIR}",
            "\n",
            f"From file: {__name__}",
        )

    except Exception as e:
        print(
            f"Failed importing settings from local config...{RESULTS_DIR} because {e}"
        )

# import configparser
# config = configparser.ConfigParser()
# config['DEFAULT'] = {'A': 1}
