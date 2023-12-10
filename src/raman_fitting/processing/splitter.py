from typing import Dict
import numpy as np

from pydantic import BaseModel
from .spectrum_template import SpectrumData

SPECTRUM_WINDOWS = {
    "full": {"min": 200, "max": 3600},
    "full_1st_2nd": {"min": 800, "max": 3500},
    "low": {"min": 150, "max": 850, "extra_margin": 10},
    "1st_order": {"min": 900, "max": 2000},
    "mid": {"min": 1850, "max": 2150, "extra_margin": 10},
    "2nd_order": {"min": 2150, "max": 3380},
    "normalization": {"min": 1500, "max": 1675, "extra_margin": 10},
}


class SpectrumWindow(BaseModel):
    name: str
    min: int
    max: int
    extra_margin: int = 20


def get_default_spectrum_windows() -> Dict[str, SpectrumWindow]:
    windows = {}
    for window_name, window_config in SPECTRUM_WINDOWS.items():
        windows[window_name] = SpectrumWindow(name=window_name, **window_config)
    return windows


def split_spectrum_data_in_windows(
    ramanshift, intensity, spec_windows=None, label=None
) -> Dict[str, SpectrumData]:
    """
    For splitting of spectra into the several SpectrumWindows,
    the names of the windows are taken from SpectrumWindows
    and set as attributes to the instance.
    """

    if spec_windows is None:
        spec_windows = get_default_spectrum_windows()
    windows_data = {}
    for window_name, window in spec_windows.items():
        # find indices of window in ramanshift array
        ind = (ramanshift >= np.min(window.min)) & (ramanshift <= np.max(window.max))
        window_lbl = f"window_{window_name}"
        if label is not None:
            window_lbl = f"{label}_{window_lbl}"
        _data = {
            "ramanshift": ramanshift[ind],
            "intensity": intensity[ind],
            "label": window_lbl,
            "window_name": window_name,
        }
        windows_data[window_lbl] = SpectrumData(**_data)
    return windows_data
