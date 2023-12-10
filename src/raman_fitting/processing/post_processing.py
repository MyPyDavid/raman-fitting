import logging

import numpy as np

from .baseline_subtraction import BaselineSubtractorNormalizer
from .filter import savgol_filter
from .despiker import Despiker

logger = logging.getLogger(__name__)

POST_PROCESS_METHODS = [
    ("filter_data", "raw", "filtered"),
    ("despike", "filtered", "despiked"),
    ("baseline_correction", "despiked", "clean_data"),
]


class SpectrumMethodsMixin:
    def split_data(self, on_lbl="filtered"):
        _r, _int, _lbl = self.register.get(on_lbl)  # unpacking data from register
        for windowname, limits in self.windows.items():
            ind = (_r >= np.min(limits)) & (_r <= np.max(limits))
            _intslice = _int[ind]
            label = f"{_lbl}_window_{windowname}"
            self.register_spectrum(_r, _intslice, label)

    def spectrum_methods_delegator(self):
        for method, on_lbl, out_lbl in POST_PROCESS_METHODS:
            try:
                breakpoint()
                getattr(self, method)(on_lbl=on_lbl, out_lbl=out_lbl)
            except Exception as exc:
                logger.error(
                    f"spectrum_methods_delegator, {self._qcnm} {method} failed for {self.file} with {exc}"
                )

        self.set_clean_data_df()
        self.set_df_from_register()

    def filter_data(self, on_lbl="raw", out_lbl="filtered"):
        _r, _int, _lbl = self.register.get(on_lbl)
        logger.debug(f"{self.file} try to filter len int({len(_int)}),({type(_int)})")
        filtered_intensity = savgol_filter(intensity=_int)
        self.filtered_intensity = filtered_intensity
        self.register_spectrum(_r, filtered_intensity, out_lbl)

    def despike(self, on_lbl="filtered", out_lbl="despiked"):
        _r, _int, _lbl = self.register.get(on_lbl)
        _despike = Despiker(_int)  # IDEA check for nan in array
        self._despike = _despike
        self.register_spectrum(_r, _despike.despiked_intensity, out_lbl)

    def baseline_correction(self, on_lbl="despiked", out_lbl="clean_data"):
        _r, _int, _lbl = self.register.get(on_lbl)
        _baseline_corrected = BaselineSubtractorNormalizer(_r, _int, label="despiked")
        self._baseline_corrected = _baseline_corrected

        _fullspec = _baseline_corrected.norm_data["full"]
        self.register_spectrum(_fullspec.ramanshift, _fullspec.intensity, out_lbl)
        self.clean_data = _baseline_corrected.norm_data
