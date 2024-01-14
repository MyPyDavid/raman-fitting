from pathlib import Path
from typing import Dict

from pydantic import BaseModel, DirectoryPath, Field, ValidationInfo, model_validator

from pydantic_settings import BaseSettings


EXPORT_FOLDER_NAMES = {
    "plots": "fitting_plots",
    "components": "fitting_components",
    "raw_data": "raw_data",
}


class ExportPathSettings(BaseModel):
    destination_dir: DirectoryPath
    plots: DirectoryPath
    components: DirectoryPath
    raw_data: DirectoryPath


def get_default_path_settings(*args, **kwargs):
    # breakpoint()
    pass


class Settings(BaseSettings):
    auth_key: str = Field(validation_alias="my_auth_key")
    default_models: Path = Field(alias="my_api_key")

    destination_dir: DirectoryPath
    export_folder_names_mapping: ExportPathSettings = Field(
        default=get_default_path_settings
    )

    @model_validator(mode="after")
    @classmethod
    def set_export_path_settings(self, info: ValidationInfo):
        destination_dir_plots: DirectoryPath = self.destination_dir.joinpath(
            EXPORT_FOLDER_NAMES["plots"]
        )
        self.destination_dir_plots = destination_dir_plots
        destination_dir_components: DirectoryPath = self.destination_dir.joinpath(
            EXPORT_FOLDER_NAMES["components"]
        )
        self.destination_dir_components = destination_dir_components
        destination_dir_raw_data: DirectoryPath = self.destination_dir.joinpath(
            EXPORT_FOLDER_NAMES["raw_data"]
        )
        self.destination_dir_raw_data = destination_dir_raw_data


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
