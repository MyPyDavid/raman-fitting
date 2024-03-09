from typing import Dict, Any
import numpy as np

from pydantic import BaseModel, model_validator, Field
from .spectrum import SpectrumData
from .deconvolution.spectrum_regions import (
    SpectrumWindowLimits,
    WindowNames,
    get_default_regions_from_toml_files,
)


class SplittedSpectrum(BaseModel):
    spectrum: SpectrumData
    window_limits: Dict[str, SpectrumWindowLimits] = Field(None, init_var=None)
    spec_regions: Dict[str, SpectrumData] = Field(None, init_var=None)
    info: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def process_spectrum(self) -> "SplittedSpectrum":
        if self.window_limits is None:
            window_limits = get_default_spectrum_window_limits()
            self.window_limits = window_limits

        if self.spec_regions is not None:
            return self
        spec_regions = split_spectrum_data_in_regions(
            self.spectrum.ramanshift,
            self.spectrum.intensity,
            spec_window_limits=self.window_limits,
            label=self.spectrum.label,
        )
        self.spec_regions = spec_regions
        return self

    def get_window(self, window_name: WindowNames):
        window_name = WindowNames(window_name)
        spec_window_keys = [
            i for i in self.spec_regions.keys() if window_name.name in i
        ]
        if not len(spec_window_keys) == 1:
            raise ValueError(f"Key {window_name} not in {spec_window_keys}")
        spec_window_key = spec_window_keys[0]
        return self.spec_regions[spec_window_key]


def get_default_spectrum_window_limits(
    regions_mapping: Dict = None,
) -> Dict[str, SpectrumWindowLimits]:
    if regions_mapping is None:
        regions_mapping = get_default_regions_from_toml_files()
    regions = {}
    for window_name, window_config in regions_mapping.items():
        regions[window_name] = SpectrumWindowLimits(name=window_name, **window_config)
    return regions


def split_spectrum_data_in_regions(
    ramanshift: np.array, intensity: np.array, spec_window_limits=None, label=None
) -> Dict[str, SpectrumData]:
    """
    For splitting of spectra into the several SpectrumWindowLimits,
    the names of the regions are taken from SpectrumWindowLimits
    and set as attributes to the instance.
    """

    if spec_window_limits is None:
        spec_window_limits = get_default_spectrum_window_limits()
    spec_regions = {}
    for window_name, window in spec_window_limits.items():
        # find indices of window in ramanshift array
        ind = (ramanshift >= np.min(window.min)) & (ramanshift <= np.max(window.max))
        window_lbl = f"window_{window_name}"
        if label is not None and label not in window_lbl:
            window_lbl = f"{label}_{window_lbl}"
        _data = {
            "ramanshift": ramanshift[ind],
            "intensity": intensity[ind],
            "label": window_lbl,
            "window_name": window_name,
        }
        spec_regions[window_lbl] = SpectrumData(**_data)
    return spec_regions
