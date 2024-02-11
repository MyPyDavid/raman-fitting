from pathlib import Path
from typing import Dict
import tempfile
from enum import StrEnum, auto

from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    Field,
    model_validator,
)

from pydantic_settings import BaseSettings

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.deconvolution.base_model import (
    get_models_and_peaks_from_definitions,
)

PACKAGE_NAME = "raman_fitting"
CURRENT_FILE: Path = Path(__file__).resolve()
PACKAGE_ROOT: Path = CURRENT_FILE.parent.parent
DEFAULT_MODELS_DIR: Path = CURRENT_FILE.parent / "default_models"
# MODEL_DIR: Path = PACKAGE_ROOT / "deconvolution_models"
EXAMPLE_FIXTURES: Path = PACKAGE_ROOT / "example_fixtures"

# Home dir from pathlib.Path for storing the results
USER_HOME_PACKAGE: Path = Path.home() / PACKAGE_NAME
# pyramdeconv is the new version package name

# Optional local configuration file
USER_LOCAL_CONFIG_FILE: Path = USER_HOME_PACKAGE / f"{PACKAGE_NAME}/toml"

INDEX_FILE_NAME = f"{PACKAGE_NAME}_index.csv"
# Storage file of the index
USER_INDEX_FILE_PATH: Path = USER_HOME_PACKAGE / INDEX_FILE_NAME

TEMP_DIR = tempfile.TemporaryDirectory()
TEMP_RESULTS_DIR: Path = Path(TEMP_DIR.name)

CLEAN_SPEC_WINDOW_NAME_PREFIX = "savgol_filter_raw_window_"

ERROR_MSG_TEMPLATE = "{sample_group} {sampleid}: {msg}"


class InternalPathSettings(BaseModel):
    settings_file: FilePath = Field(CURRENT_FILE)
    package_root: DirectoryPath = Field(PACKAGE_ROOT)
    default_models_dir: DirectoryPath = Field(DEFAULT_MODELS_DIR)
    example_fixtures: DirectoryPath = Field(EXAMPLE_FIXTURES)
    temp_dir: DirectoryPath = Field(TEMP_RESULTS_DIR)


EXPORT_FOLDER_NAMES = {
    "plots": "fitting_plots",
    "components": "fitting_components",
    "raw_data": "raw_data",
}


class RunModes(StrEnum):
    NORMAL = auto()
    TESTING = auto()
    DEBUG = auto()
    MAKE_INDEX = auto()
    MAKE_EXAMPLES = auto()


RUN_MODE_PATHS = {
    "testing": {
        "RESULTS_DIR": TEMP_RESULTS_DIR,
        "DATASET_DIR": EXAMPLE_FIXTURES,
        "USER_CONFIG_FILE": EXAMPLE_FIXTURES / f"{PACKAGE_NAME}.toml",
        "INDEX_FILE": TEMP_RESULTS_DIR / f"{PACKAGE_NAME}_index.csv",
    },
    "make_examples": {
        "RESULTS_DIR": USER_HOME_PACKAGE / "make_examples",
        "DATASET_DIR": EXAMPLE_FIXTURES,
        "USER_CONFIG_FILE": EXAMPLE_FIXTURES / f"{PACKAGE_NAME}.toml",
        "INDEX_FILE": TEMP_RESULTS_DIR / f"{PACKAGE_NAME}_index.csv",
    },
    "normal": {
        "RESULTS_DIR": USER_HOME_PACKAGE / "results",
        "DATASET_DIR": USER_HOME_PACKAGE / "datafiles",
        "USER_CONFIG_FILE": USER_HOME_PACKAGE / "raman_fitting.toml",
        "INDEX_FILE": TEMP_RESULTS_DIR / f"{PACKAGE_NAME}_index.csv",
    },
}


class ExportPathSettings(BaseModel):
    destination_dir: DirectoryPath
    plots: DirectoryPath = Field(None, validate_default=False)
    components: DirectoryPath = Field(None, validate_default=False)
    raw_data: DirectoryPath = Field(None, validate_default=False)

    @model_validator(mode="after")
    def set_export_path_settings(self) -> "ExportPathSettings":
        plots: DirectoryPath = self.destination_dir.joinpath(
            EXPORT_FOLDER_NAMES["plots"]
        )
        self.plots = plots
        components: DirectoryPath = self.destination_dir.joinpath(
            EXPORT_FOLDER_NAMES["components"]
        )
        self.components = components
        raw_data: DirectoryPath = self.destination_dir.joinpath(
            EXPORT_FOLDER_NAMES["raw_data"]
        )
        self.raw_data = raw_data


def get_default_path_settings(*args, **kwargs):
    # breakpoint()
    export_paths = ExportPathSettings(**{"destination_dir": USER_HOME_PACKAGE})
    return export_paths


class Settings(BaseSettings):
    default_models: Dict[str, Dict[str, BaseLMFitModel]] = Field(
        default_factory=get_models_and_peaks_from_definitions,
        alias="my_default_models",
        init_var=False,
        validate_default=False,
    )

    destination_dir: DirectoryPath = Field(USER_HOME_PACKAGE)
    export_folder_names_mapping: ExportPathSettings = Field(
        default_factory=get_default_path_settings
    )
    internal_paths: InternalPathSettings = Field(default_factory=InternalPathSettings)

    @staticmethod
    def get_run_mode_paths(run_mode: str) -> Dict[str, Path]:
        if run_mode not in RUN_MODE_PATHS:
            raise ValueError(f"Choice of run_mode {run_mode} not supported.")
        dest_dirs = RUN_MODE_PATHS[run_mode]
        dest_dirs["INDEX_FILE"] = dest_dirs["RESULTS_DIR"] / INDEX_FILE_NAME
        return dest_dirs


def sample_settings(sample_grp: str) -> Dict[str, Path]:
    # move to settings
    dest_grp_dir = Path(
        sample_grp.DestDir.unique()[0]
    )  # takes one destination directory from Sample Groups
    dest_fit_plots = dest_grp_dir.joinpath("Fitting_Plots")
    dest_fit_comps = dest_grp_dir.joinpath("Fitting_Components")
    dest_fit_comps.mkdir(parents=True, exist_ok=True)

    dest_raw_data_dir = dest_grp_dir.joinpath("Raw_Data")
    dest_raw_data_dir.mkdir(parents=True, exist_ok=True)

    export_info = {
        "DestGrpDir": dest_grp_dir,
        "DestFittingPlots": dest_fit_plots,
        "DestFittingComps": dest_fit_comps,
        "DestRaw": dest_raw_data_dir,
    }
    return export_info
