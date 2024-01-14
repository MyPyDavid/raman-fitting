from enum import Enum
from typing import Dict, Any
import numpy as np

from pydantic import BaseModel, model_validator, Field
from .spectrum import SpectrumData


PLOT_WINDOW_AXES = {
    "full": (0, 0),
    "low": (0, 1),
    "1st_order": (0, 2),
    "mid": (1, 1),
    "2nd_order": (1, 2),
    "normalization": (1, 0),
}

SPECTRUM_WINDOWS_LIMITS = {
    "full": {"min": 200, "max": 3600},
    "full_1st_2nd": {"min": 800, "max": 3500},
    "low": {"min": 150, "max": 850, "extra_margin": 10},
    "first_order": {"min": 900, "max": 2000},
    "mid": {"min": 1850, "max": 2150, "extra_margin": 10},
    "second_order": {"min": 2150, "max": 3380},
    "normalization": {"min": 1500, "max": 1675, "extra_margin": 10},
}


class WindowNameEnum(str, Enum):
    full = "full"
    full_1st_2nd = "full_1st_2nd"
    low = "low"
    first_order = "first_order"
    mid = "mid"
    second_order = "second_order"
    normalization = "normalization"


class SpectrumWindowLimits(BaseModel):
    name: WindowNameEnum
    min: int
    max: int
    extra_margin: int = 20


class SplittedSpectrum(BaseModel):
    spectrum: SpectrumData
    window_limits: Dict[str, SpectrumWindowLimits] = Field(None, init_var=None)
    spec_windows: Dict[str, SpectrumData] = Field(None, init_var=None)
    info: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def process_spectrum(self) -> "SplittedSpectrum":
        if self.window_limits is None:
            window_limits = get_default_spectrum_window_limits()
            self.window_limits = window_limits

        if self.spec_windows is not None:
            return self
        spec_windows = split_spectrum_data_in_windows(
            self.spectrum.ramanshift,
            self.spectrum.intensity,
            spec_window_limits=self.window_limits,
            label=self.spectrum.label,
        )
        self.spec_windows = spec_windows
        return self


def get_default_spectrum_window_limits() -> Dict[str, SpectrumWindowLimits]:
    windows = {}
    for window_name, window_config in SPECTRUM_WINDOWS_LIMITS.items():
        windows[window_name] = SpectrumWindowLimits(name=window_name, **window_config)
    return windows


def split_spectrum_data_in_windows(
    ramanshift: np.array, intensity: np.array, spec_window_limits=None, label=None
) -> Dict[str, SpectrumData]:
    """
    For splitting of spectra into the several SpectrumWindowLimits,
    the names of the windows are taken from SpectrumWindowLimits
    and set as attributes to the instance.
    """

    if spec_window_limits is None:
        spec_window_limits = get_default_spectrum_window_limits()
    spec_windows = {}
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
        spec_windows[window_lbl] = SpectrumData(**_data)
    return spec_windows
