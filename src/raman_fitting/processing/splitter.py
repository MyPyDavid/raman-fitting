from typing import Dict
import numpy as np

from pydantic import BaseModel

SPECTRUM_WINDOWS = [
    {"name": "full", "min": 200, "max": 3600},
    {"name": "full_1st_2nd", "min": 800, "max": 3500},
    {"name": "low", "min": 150, "max": 850, "extra_margin": 10},
    {"name": "1st_order", "min": 900, "max": 2000},
    {"name": "mid", "min": 1850, "max": 2150, "extra_margin": 10},
    {"name": "2nd_order", "min": 2150, "max": 3380},
    {"name": "normalization", "min": 1500, "max": 1675, "extra_margin": 10},
]


class SpectrumWindow(BaseModel):
    name: str
    min: int
    max: int
    extra_margin: int = 20


def get_default_spectrum_windows() -> Dict[str, SpectrumWindow]:
    windows = {}
    for window_config in SPECTRUM_WINDOWS:
        windows[window_config["name"]] = SpectrumWindow(**window_config)
    return windows


def split_spectrum_data_in_windows(
    ramanshift, intensity, spec_windows=None, label=None
) -> Dict:
    """
    For splitting of spectra into the several SpectrumWindows,
    the names of the windows are taken from SpectrumWindows
    and set as attributes to the instance.
    """

    if spec_windows is None:
        spec_windows = get_default_spectrum_windows()
    windows_data = {}
    for windowname, window in spec_windows.items():
        # find indices of window in ramanshift array
        ind = (ramanshift >= np.min(window.min)) & (ramanshift <= np.max(window.max))
        window_lbl = f"window_{windowname}"
        if label is not None:
            window_lbl = f"{label}_{window_lbl}"
        _data = {"ramanshift": ramanshift[ind], "intensity": intensity[ind]}
        windows_data[window_lbl] = _data
    return windows_data
