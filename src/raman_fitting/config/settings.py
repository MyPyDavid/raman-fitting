from pathlib import Path
from typing import Dict
import tempfile
from enum import StrEnum, auto


from pydantic import (
    BaseModel,
    DirectoryPath,
    FilePath,
    ConfigDict,
    Field,
    model_validator,
)

from pydantic_settings import BaseSettings

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.deconvolution.base_model import (
    get_models_and_peaks_from_definitions,
)
from .filepath_helper import check_and_make_dirs, create_dir_or_ask_user_input


PACKAGE_NAME = "raman_fitting"
CURRENT_FILE: Path = Path(__file__).resolve()
PACKAGE_ROOT: Path = CURRENT_FILE.parent.parent
REPO_ROOT: Path = PACKAGE_ROOT.parent
INTERNAL_DEFAULT_MODELS: Path = CURRENT_FILE.parent / "default_models"
# MODEL_DIR: Path = PACKAGE_ROOT / "deconvolution_models"
INTERNAL_EXAMPLE_FIXTURES: Path = PACKAGE_ROOT / "example_fixtures"
INTERNAL_PYTEST_FIXTURES: Path = REPO_ROOT / "tests" / "test_fixtures"

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
    default_models_dir: DirectoryPath = Field(INTERNAL_DEFAULT_MODELS)
    example_fixtures: DirectoryPath = Field(INTERNAL_EXAMPLE_FIXTURES)
    pytest_fixtures: DirectoryPath = Field(INTERNAL_PYTEST_FIXTURES)
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


def get_run_mode_paths(run_mode: RunModes, user_package_home: Path = None):
    if user_package_home is None:
        user_package_home = USER_HOME_PACKAGE

    RUN_MODE_PATHS = {
        "pytest": {
            "RESULTS_DIR": TEMP_RESULTS_DIR,
            "DATASET_DIR": INTERNAL_EXAMPLE_FIXTURES,
            "USER_CONFIG_FILE": INTERNAL_EXAMPLE_FIXTURES / f"{PACKAGE_NAME}.toml",
            "INDEX_FILE": TEMP_RESULTS_DIR / f"{PACKAGE_NAME}_index.csv",
        },
        "make_examples": {
            "RESULTS_DIR": user_package_home / "make_examples",
            "DATASET_DIR": INTERNAL_EXAMPLE_FIXTURES,
            "USER_CONFIG_FILE": INTERNAL_EXAMPLE_FIXTURES / f"{PACKAGE_NAME}.toml",
            "INDEX_FILE": user_package_home
            / "make_examples"
            / f"{PACKAGE_NAME}_index.csv",
        },
        "normal": {
            "RESULTS_DIR": user_package_home / "results",
            "DATASET_DIR": user_package_home / "datafiles",
            "USER_CONFIG_FILE": user_package_home / "raman_fitting.toml",
            "INDEX_FILE": user_package_home / f"{PACKAGE_NAME}_index.csv",
        },
    }
    if run_mode not in RUN_MODE_PATHS:
        raise ValueError(f"Choice of run_mode {run_mode} not supported.")
    return RUN_MODE_PATHS[run_mode]


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
    user_config_file: Path
    index_file: Path


def initialize_run_mode_paths(
    run_mode: RunModes, user_package_home: Path = None
) -> RunModePaths:
    run_mode_paths = get_run_mode_paths(run_mode, user_package_home=user_package_home)

    # USER_HOME_PACKAGE = get_user_destination_dir(USER_HOME_PACKAGE)
    for destname, destdir in run_mode_paths.items():
        destdir = Path(destdir)
        check_and_make_dirs(destdir)
    # dest_dirs["RUN_MODE"] = run_mode
    # breakpoint()
    return RunModePaths(RUN_MODE=run_mode, **run_mode_paths)


def create_default_package_dir_or_ask():
    return create_dir_or_ask_user_input(USER_HOME_PACKAGE)


class Settings(BaseSettings):
    default_models: Dict[str, Dict[str, BaseLMFitModel]] = Field(
        default_factory=get_models_and_peaks_from_definitions,
        alias="my_default_models",
        init_var=False,
        validate_default=False,
    )

    destination_dir: DirectoryPath = Field(
        default_factory=create_default_package_dir_or_ask
    )
    # export_folder_names_mapping: ExportPathSettings = Field(
    #     default_factory=get_default_path_settings,
    #     init_var=False,
    #     validate_default=False,
    # )
    internal_paths: InternalPathSettings = Field(default_factory=InternalPathSettings)
