from typing import Dict, Any
import numpy as np

from pydantic import BaseModel, model_validator, Field
from .spectrum import SpectrumData
from .deconvolution.spectrum_regions import (
    SpectrumRegionLimits,
    RegionNames,
    get_default_regions_from_toml_files,
    SpectrumRegionsLimitsSet,
)


def get_default_spectrum_region_limits(
    regions_mapping: SpectrumRegionsLimitsSet | None = None,
) -> SpectrumRegionsLimitsSet:
    if regions_mapping is None:
        regions_mapping = get_default_regions_from_toml_files()
    regions = {}
    for region_name, region_config in regions_mapping:
        regions[region_name] = SpectrumRegionLimits(
            name=region_name, **region_config.model_dump(exclude={"name"})
        )
    return regions


class SplitSpectrum(BaseModel):
    spectrum: SpectrumData
    region_limits: SpectrumRegionsLimitsSet = Field(
        default_factory=get_default_spectrum_region_limits
    )
    split_spectra: list[SpectrumData] = Field(default_factory=list)
    info: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def spit_spectrum_into_regions(self) -> "SplitSpectrum":
        if not all(isinstance(i, SpectrumData) for i in self.split_spectra):
            raise ValueError("Not all spectrum regions are valid SpectrumData objects.")

        self.split_spectra = split_spectrum_data_in_regions(
            self.spectrum,
            spec_region_limits=self.region_limits,
        )

        return self

    def get_spec_for_region(self, region_name: RegionNames):
        if not self.split_spectra:
            raise ValueError("Missing spectrum regions.")
        region_name = RegionNames(region_name)
        _regions = set()
        for region, spec in self:
            if region is region_name:
                return spec
            _regions.add(region)
        else:
            raise ValueError(f"Key {region_name} not in {_regions}")

    def __iter__(self) -> tuple[RegionNames, SpectrumData]:
        if self.split_spectra is None:
            raise ValueError("Missing spectrum regions.")
        for spectrum in self.split_spectra:
            yield spectrum.region_name, spectrum


def split_spectrum_data_in_regions(
    spectrum: SpectrumData,
    spec_region_limits: SpectrumRegionsLimitsSet | None = None,
) -> list[SpectrumData]:
    """
    For splitting of spectra into the several SpectrumRegionLimits,
    the names of the regions are taken from SpectrumRegionLimits
    and set as attributes to the instance.
    """
    ramanshift = spectrum.ramanshift
    intensity = spectrum.intensity
    label = spectrum.label
    source = spectrum.source
    processing_steps = spectrum.processing_steps.copy()

    if spec_region_limits is None:
        spec_region_limits = get_default_regions_from_toml_files()()
    split_spectra = []
    for region in spec_region_limits:
        # find indices of region in ramanshift array
        ind = (ramanshift >= np.min(region.min)) & (ramanshift <= np.max(region.max))
        region_lbl = f"region_{region.name}"
        if label is not None and label not in region_lbl:
            region_lbl = f"{label}_{region_lbl}"

        new_processing_step = (
            f"spectrum region {region.name} split from {spectrum.region_name} "
            f"with limits {region.min} - {region.max}"
        )
        _data = {
            "ramanshift": ramanshift[ind],
            "intensity": intensity[ind],
            "label": region_lbl,
            "region_name": region.name,
            "source": source,
            "processing_steps": processing_steps,
        }
        spectrum_region = SpectrumData(**_data)
        spectrum_region.add_processing_step(new_processing_step)
        split_spectra.append(spectrum_region)

    return split_spectra
