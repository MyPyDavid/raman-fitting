from dataclasses import dataclass
import logging
from pathlib import Path
import tempfile


import raman_fitting


logger = logging.getLogger(__name__)

TEMP_DIR = tempfile.TemporaryDirectory()


@dataclass
class FilePathConfig:
    CONFIG_FILE: Path = Path(__file__).resolve()
    PACKAGE_ROOT: Path = CONFIG_FILE.parent.parent
    DEFAULT_MODELS_DIR: Path = CONFIG_FILE.parent / "default_models"
    MODEL_DIR: Path = PACKAGE_ROOT / "deconvolution_models"
    EXAMPLE_FIXTURES: Path = PACKAGE_ROOT / "example_fixtures"

    # Home dir from pathlib.Path for storing the results
    USER_PACKAGE_HOME: Path = (
        Path.home() / f".{raman_fitting.__package_name__}"
    )  # pyramdeconv is the new version package name

    # Optional local configuration file
    LOCAL_CONFIG_FILE: Path = USER_PACKAGE_HOME / "local_config.py"

    # Storage file of the index
    INDEX_FILE_NAME: str = f"{raman_fitting.__package_name__}_index.csv"
    INDEX_FILE_PATH: Path = USER_PACKAGE_HOME / INDEX_FILE_NAME

    TEST_RESULTS_DIR: Path = Path(TEMP_DIR.name)

    CONFIG = {
        "defaults": {
            "CONFIG_FILE": CONFIG_FILE,
            "PACKAGE_ROOT": PACKAGE_ROOT,
            "MODEL_DIR": MODEL_DIR,
            "USER_PACKAGE_HOME": USER_PACKAGE_HOME,
            "INDEX_FILE_NAME": INDEX_FILE_NAME,
            "INDEX_FILE": INDEX_FILE_PATH,
        },
        "testing": {
            "RESULTS_DIR": TEST_RESULTS_DIR,
            "DATASET_DIR": EXAMPLE_FIXTURES,
            "USER_CONFIG_FILE": EXAMPLE_FIXTURES / "raman_fitting.toml",
        },
        "make_examples": {
            "RESULTS_DIR": USER_PACKAGE_HOME / "make_examples",
            "DATASET_DIR": EXAMPLE_FIXTURES,
            "USER_CONFIG_FILE": EXAMPLE_FIXTURES / "raman_fitting.toml",
        },
        "normal": {
            "RESULTS_DIR": USER_PACKAGE_HOME / "results",
            "DATASET_DIR": USER_PACKAGE_HOME / "datafiles",
            "USER_CONFIG_FILE": USER_PACKAGE_HOME / "raman_fitting.toml",
        },
    }
    CONFIG["debug"] = CONFIG["testing"]
