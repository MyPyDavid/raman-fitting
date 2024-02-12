from pathlib import Path
from typing import Dict
import tempfile
from enum import StrEnum, auto

from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    NewPath,
    ConfigDict,
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
REPO_ROOT: Path = PACKAGE_ROOT.parent
DEFAULT_MODELS_DIR: Path = CURRENT_FILE.parent / "default_models"
# MODEL_DIR: Path = PACKAGE_ROOT / "deconvolution_models"
EXAMPLE_FIXTURES: Path = PACKAGE_ROOT / "example_fixtures"
PYTEST_FIXUTRES: Path = REPO_ROOT / "tests" / "test_fixtures"

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

# TODO fix label on clean processed spectrum to simple window name
CLEAN_SPEC_WINDOW_NAME_PREFIX = "savgol_filter_raw_window_"

ERROR_MSG_TEMPLATE = "{sample_group} {sampleid}: {msg}"


class InternalPathSettings(BaseModel):
    settings_file: FilePath = Field(CURRENT_FILE)
    package_root: DirectoryPath = Field(PACKAGE_ROOT)
    default_models_dir: DirectoryPath = Field(DEFAULT_MODELS_DIR)
    example_fixtures: DirectoryPath = Field(EXAMPLE_FIXTURES)
    pytest_fixtures: DirectoryPath = Field(PYTEST_FIXUTRES)
    temp_dir: DirectoryPath = Field(TEMP_RESULTS_DIR)


EXPORT_FOLDER_NAMES = {
    "plots": "fitting_plots",
    "components": "fitting_components",
    "raw_data": "raw_data",
}


class RunModes(StrEnum):
    NORMAL = auto()
    PYTEST = auto()
    MAKE_EXAMPLES = auto()
    DEBUG = auto()
    MAKE_INDEX = auto()


RUN_MODE_PATHS = {
    "pytest": {
        "RESULTS_DIR": TEMP_RESULTS_DIR,
        "DATASET_DIR": EXAMPLE_FIXTURES,
        "USER_CONFIG_FILE": EXAMPLE_FIXTURES / f"{PACKAGE_NAME}.toml",
        "INDEX_FILE": TEMP_RESULTS_DIR / f"{PACKAGE_NAME}_index.csv",
    },
    "make_examples": {
        "RESULTS_DIR": USER_HOME_PACKAGE / "make_examples",
        "DATASET_DIR": EXAMPLE_FIXTURES,
        "USER_CONFIG_FILE": EXAMPLE_FIXTURES / f"{PACKAGE_NAME}.toml",
        "INDEX_FILE": USER_HOME_PACKAGE / "make_examples" / f"{PACKAGE_NAME}_index.csv",
    },
    "normal": {
        "RESULTS_DIR": USER_HOME_PACKAGE / "results",
        "DATASET_DIR": USER_HOME_PACKAGE / "datafiles",
        "USER_CONFIG_FILE": USER_HOME_PACKAGE / "raman_fitting.toml",
        "INDEX_FILE": USER_HOME_PACKAGE / f"{PACKAGE_NAME}_index.csv",
    },
}


class ExportPathSettings(BaseModel):
    results_dir: Path
    plots: DirectoryPath = Field(None, validate_default=False)
    components: DirectoryPath = Field(None, validate_default=False)
    raw_data: DirectoryPath = Field(None, validate_default=False)

    @model_validator(mode="after")
    def set_export_path_settings(self) -> "ExportPathSettings":
        if not self.results_dir.is_dir():
            self.results_dir.mkdir(exist_ok=True, parents=True)

        plots: DirectoryPath = self.results_dir.joinpath(EXPORT_FOLDER_NAMES["plots"])
        self.plots = plots
        components: DirectoryPath = self.results_dir.joinpath(
            EXPORT_FOLDER_NAMES["components"]
        )
        self.components = components
        raw_data: DirectoryPath = self.results_dir.joinpath(
            EXPORT_FOLDER_NAMES["raw_data"]
        )
        self.raw_data = raw_data


# def get_default_path_settings(*args, **kwargs) -> ExportPathSettings:
#     # breakpoint()
#     return ExportPathSettings(results_dir=USER_HOME_PACKAGE)


class RunModePaths(BaseModel):
    model_config = ConfigDict(alias_generator=str.upper)

    run_mode: RunModes
    results_dir: DirectoryPath
    dataset_dir: DirectoryPath
    user_config_file: FilePath | NewPath
    index_file: FilePath | NewPath


def get_run_mode_paths(run_mode: RunModes) -> RunModePaths:
    if run_mode not in RUN_MODE_PATHS:
        raise ValueError(f"Choice of run_mode {run_mode} not supported.")
    dest_dirs = RUN_MODE_PATHS[run_mode]
    dest_dirs["RUN_MODE"] = run_mode
    # breakpoint()
    return RunModePaths(**dest_dirs)


class Settings(BaseSettings):
    default_models: Dict[str, Dict[str, BaseLMFitModel]] = Field(
        default_factory=get_models_and_peaks_from_definitions,
        alias="my_default_models",
        init_var=False,
        validate_default=False,
    )

    destination_dir: DirectoryPath = Field(USER_HOME_PACKAGE)
    # export_folder_names_mapping: ExportPathSettings = Field(
    #     default_factory=get_default_path_settings,
    #     init_var=False,
    #     validate_default=False,
    # )
    internal_paths: InternalPathSettings = Field(default_factory=InternalPathSettings)
