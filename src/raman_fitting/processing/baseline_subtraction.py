import logging
from typing import Optional

import numpy as np
from scipy.stats import linregress

from .splitter import get_default_spectrum_windows, split_spectrum_data_in_windows
from .spectrum_template import SpectrumData

logger = logging.getLogger(__name__)


def subtract_baseline_per_window(spec, label, windows_data, window_limits):
    ramanshift = spec.ramanshift
    intensity = spec.intensity
    window_name = spec.window_name
    if not ramanshift.any():
        return intensity, (0, 0)
    # breakpoint()
    lbl_1st_order = list(filter(lambda x: "1st_order" in x, windows_data.keys()))
    if any(i in label for i in ("full", "norm")) and lbl_1st_order:
        i_fltrd_dspkd_fit = windows_data.get(lbl_1st_order[0]).intensity
    else:
        i_fltrd_dspkd_fit = intensity
    window_config = window_limits.get(window_name)

    bl_linear = linregress(
        ramanshift[[0, -1]],
        [
            np.mean(i_fltrd_dspkd_fit[0 : window_config.min]),
            np.mean(i_fltrd_dspkd_fit[window_config.max : :]),
        ],
    )
    i_blcor = intensity - (bl_linear[0] * ramanshift + bl_linear[1])
    return i_blcor, bl_linear


def get_normalization_factor(data, norm_method="simple") -> float:
    try:
        if norm_method == "simple":
            normalization_intensity = np.nanmax(data["normalization"].intensity)
        elif norm_method == "fit":
            raise NotImplementedError("NormalizeFit not yet implemented")
            # IDEA not implemented
            # normalization = NormalizeFit(
            #     self.blcorr_data["1st_order"], plotprint=False
            # )  # IDEA still implement this NormalizeFit
            # normalization_intensity = normalization["IG"]
        else:
            logger.warning(f"unknown normalization method {norm_method}")
            normalization_intensity = 1
    except Exception as exc:
        logger.error(f"normalization error {exc}")
        normalization_intensity = 1

    return normalization_intensity


def normalize_data(windows_data, norm_factor, label: Optional[str] = None) -> dict:
    ret = {}
    for window_name, spec in windows_data.items():
        norm_label = f"norm_blcorr_{window_name}"
        if label:
            norm_label = f"{label}_{norm_label}"
        _data = SpectrumData(
            spec.ramanshift, spec.intensity * norm_factor, norm_label, window_name
        )
        ret.update(**{window_name: _data})
    return ret


def subtract_loop(windows_data: dict, window_limits: dict, label=None):
    _blcorr = {}
    _info = {}
    for window_name, spec in windows_data.items():
        blcorr_int, blcorr_lin = subtract_baseline_per_window(
            spec, window_name, windows_data, window_limits
        )
        if label:
            label = f"blcorr_{label}"
        _data = SpectrumData(spec.ramanshift, blcorr_int, label, window_name)
        _blcorr.update(**{window_name: _data})
        _info.update(**{window_name: blcorr_lin})
    return _blcorr, _info


class BaselineSubtractorNormalizer:
    """
    For baseline subtraction as well as normalization of a spectrum
    """

    def __init__(self, ramanshift: np.array, intensity: np.array, label: str = None):
        self._ramanshift = ramanshift
        self._intensity = intensity
        self._label = label
        self.windows_data = split_spectrum_data_in_windows(
            ramanshift=ramanshift, intensity=intensity, label=label
        )
        self.window_limits = get_default_spectrum_windows()
        blcorr_data, blcorr_info = subtract_loop(
            self.windows_data, self.window_limits, label=self._label
        )
        self.blcorr_data = blcorr_data
        self.blcorr_info = blcorr_info
        normalization_intensity = get_normalization_factor(self.blcorr_data)
        self.norm_factor = 1 / normalization_intensity
        self.norm_data = normalize_data(self.blcorr_data, self.norm_factor)
