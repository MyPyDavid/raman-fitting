from __future__ import annotations
from raman_fitting.utils.compat import StrEnum

from pydantic import computed_field

from loguru import logger
from pydantic import BaseModel, ValidationError
from raman_fitting.config.load_config_from_toml import load_config_from_toml_files


# Placeholder for RegionNames, will be updated later
class RegionNames(StrEnum):
    pass


class SpectrumRegionLimits(BaseModel):
    name: RegionNames | str
    min: int
    max: int
    extra_margin: int = 20

    model_config = {"frozen": True}


class SpectrumRegionsLimitsSet(BaseModel):
    regions: list[SpectrumRegionLimits]

    @computed_field
    @property
    def regions_by_name(self) -> dict[RegionNames, SpectrumRegionLimits]:
        return {i.name: i for i in self.regions}

    def __iter__(self):
        return iter(sorted(self.regions, key=lambda x: x.min, reverse=True))

    def __getitem__(self, item) -> SpectrumRegionLimits:
        return self.regions_by_name[item]

    def __len__(self):
        return len(self.regions)

    def __contains__(self, item):
        return item in self.regions or item in [region.name for region in self.regions]


def get_default_regions_from_toml_files() -> SpectrumRegionsLimitsSet:
    toml_config = load_config_from_toml_files()
    default_regions_from_file = toml_config.get("spectrum", {}).get("regions", {})
    default_regions = []
    for region_name, region_data in default_regions_from_file.items():
        try:
            if "limits" not in region_data:
                raise ValueError(
                    f"Region definition for {region_name} requires limits. Missing from {region_data.keys()}"
                )
            region_limits = region_data.get("limits", {})

            valid_region = SpectrumRegionLimits(name=region_name, **region_limits)
            default_regions.append(valid_region)
        except ValidationError as e:
            logger.error(f"Region definition for {region_name} is not valid: {e}")
            raise e from e

    return SpectrumRegionsLimitsSet(regions=default_regions)


# Assuming get_default_regions_from_toml_files() returns a dictionary
DEFAULT_REGION_NAMES_FROM_TOML = {i.name for i in get_default_regions_from_toml_files()}
DEFAULT_REGION_NAME_FALLBACK = {"full", "first_order", "second_order"}
DEFAULT_REGION_NAME_KEYS = (
    DEFAULT_REGION_NAMES_FROM_TOML or DEFAULT_REGION_NAME_FALLBACK
)


class RegionNamesMeta(type(StrEnum)):
    def __new__(metacls, cls, bases, classdict):
        for key in DEFAULT_REGION_NAME_KEYS:
            classdict[key.upper()] = key
        return super().__new__(metacls, cls, bases, classdict)


class RegionNames(StrEnum, metaclass=RegionNamesMeta):  # noqa: F811
    @classmethod
    def choices(cls) -> list[str]:
        return [member.value for member in cls]


# Update forward references to ensure RegionNames is properly defined
SpectrumRegionLimits.model_rebuild(_types_namespace={"RegionNames": RegionNames})
