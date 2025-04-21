from functools import cached_property
from typing import Dict, Any
import numpy as np
from attrs import define

from pydantic import BaseModel, Field, computed_field, ConfigDict

from .spectrum import SpectrumData
from .deconvolution.spectrum_regions import (
    SpectrumRegionLimits,
    RegionNames,
    get_default_regions_from_toml_files,
    SpectrumRegionsLimitsSet,
)
from ..imports.files.models import RamanFileInfo


@define
class SpectrumFileRegionSelection:
    file: RamanFileInfo
    region: RegionNames


def get_default_spectrum_region_limits(
    regions_mapping: SpectrumRegionsLimitsSet | None = None,
) -> SpectrumRegionsLimitsSet:
    if regions_mapping is None:
        regions_mapping = get_default_regions_from_toml_files()
    regions = []
    for region_name, region_config in regions_mapping:
        regions.append(
            SpectrumRegionLimits(
                name=region_name, **region_config.model_dump(exclude={"name"})
            )
        )
    return SpectrumRegionsLimitsSet(regions=regions)


class SplitSpectrum(BaseModel):
    spectrum: SpectrumData = Field(repr=False)
    region_limits: SpectrumRegionsLimitsSet = Field(
        default_factory=get_default_spectrum_region_limits, repr=False
    )
    info: Dict[str, Any] = Field(default_factory=dict)
    split_spectra: list[SpectrumData] | None = Field(default=None, repr=False)

    model_config = ConfigDict(extra="forbid")

    @computed_field
    @cached_property
    def computed_split_spectra_from_spectrum(self) -> list[SpectrumData]:
        if self.split_spectra is not None:
            return self.split_spectra
        return split_spectrum_data_in_regions(
            self.spectrum,
            spec_region_limits=self.region_limits,
        )

    def get_spec_for_region(self, region_name: RegionNames) -> SpectrumData:
        if not self.computed_split_spectra_from_spectrum:
            raise ValueError("Missing spectrum regions.")
        region_name = RegionNames(region_name)
        _regions = set()
        for region, spec in self:
            if region is region_name:
                return spec
            _regions.add(region)
        raise ValueError(f"Key {region_name} not in {_regions}")

    def __iter__(self) -> tuple[RegionNames, SpectrumData]:
        if self.computed_split_spectra_from_spectrum is None:
            raise ValueError("Missing split spectra.")
        for spectrum in self.computed_split_spectra_from_spectrum:
            yield spectrum.region, spectrum


def split_spectrum_data_in_regions(
    spectrum: SpectrumData,
    spec_region_limits: SpectrumRegionsLimitsSet | None = None,
) -> list[SpectrumData]:
    """
    For splitting of spectra into the several SpectrumRegionLimits,
    the names of the regions are taken from SpectrumRegionLimits
    and set as attributes to the instance.
    """
    if spec_region_limits is None:
        spec_region_limits = get_default_regions_from_toml_files()()

    ramanshift = spectrum.ramanshift
    intensity = spectrum.intensity

    split_spectra = []
    for region in spec_region_limits:
        # find indices of region in ramanshift array
        ind = (ramanshift >= np.min(region.min)) & (ramanshift <= np.max(region.max))
        region_lbl = f"region_{region.name}"
        if spectrum.label is not None and spectrum.label not in region_lbl:
            region_lbl = f"{spectrum.label}_{region_lbl}"

        new_processing_step = (
            f"spectrum region {region.name} split from {spectrum.region} "
            f"with limits {region.min} - {region.max}"
        )
        spectrum_region = SpectrumData(
            ramanshift=ramanshift[ind],
            intensity=intensity[ind],
            label=region_lbl,
            region=region.name,
            source=spectrum.source,
            processing_steps=spectrum.processing_steps.copy(),
        )
        spectrum_region.add_processing_step(new_processing_step)
        split_spectra.append(spectrum_region)

    return split_spectra
