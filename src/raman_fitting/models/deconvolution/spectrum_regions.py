from enum import StrEnum
from typing import Dict

from pydantic import BaseModel
from raman_fitting.config.default_models import load_config_from_toml_files


def get_default_regions_from_toml_files() -> Dict[str, Dict[str, float]]:
    default_regions = (
        load_config_from_toml_files().get("spectrum", {}).get("regions", {})
    )
    return default_regions


RegionNames = StrEnum(
    "RegionNames", " ".join(get_default_regions_from_toml_files()), module=__name__
)


class SpectrumRegionLimits(BaseModel):
    name: RegionNames
    min: int
    max: int
    extra_margin: int = 20
