# from .logging_config import get_console_handler
import logging
from pathlib import Path
import tempfile

from raman_fitting import __package_name__

logger = logging.getLogger(__name__)

from dataclasses import dataclass


TEMP_DIR = tempfile.TemporaryDirectory()


@dataclass
class Config:
    CONFIG_FILE = Path(__file__).resolve()
    PACKAGE_ROOT = CONFIG_FILE.parent.parent
    MODEL_DIR = PACKAGE_ROOT / "deconvolution_models"
    TEST_FIXTURES = PACKAGE_ROOT / "test_fixtures"

    # Home dir from pathlib.Path for storing the results
    USER_PACKAGE_HOME = (
        Path.home() / f".{__package_name__}"
    )  # pyramdeconv is the new version package name

    # Optional local configuration file
    LOCAL_CONFIG_FILE = USER_PACKAGE_HOME / "local_config.py"

    # Storage file of the index
    INDEX_FILE_NAME = f"{__package_name__}_index.csv"

    TEST_RESULTS_DIR = Path(TEMP_DIR.name)

    CONFIG = {
        "defaults": {
            "CONFIG_FILE": CONFIG_FILE,
            "PACKAGE_ROOT": PACKAGE_ROOT,
            "MODEL_DIR": MODEL_DIR,
            "USER_PACKAGE_HOME": USER_PACKAGE_HOME,
            "INDEX_FILE_NAME": INDEX_FILE_NAME,
            "LOCAL_CONFIG_FILE": LOCAL_CONFIG_FILE,
        },
        "testing": {
            "RESULTS_DIR": TEST_RESULTS_DIR,
            "DATASET_DIR": TEST_FIXTURES,
        },
        "make_examples": {
            "RESULTS_DIR": USER_PACKAGE_HOME / "make_examples",
            "DATASET_DIR": TEST_FIXTURES,
        },
        "normal": {
            "RESULTS_DIR": USER_PACKAGE_HOME / "results",
            "DATASET_DIR": USER_PACKAGE_HOME / "datafiles",
        },
    }
    CONFIG['debug'] = CONFIG['testing']
