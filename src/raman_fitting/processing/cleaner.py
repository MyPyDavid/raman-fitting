#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import linregress

# from collections import namedtuple
from raman_fitting.processing.spectrum_template import (
    SpecTemplate,
    SpectrumWindowLimits,
    SpectrumWindows,
)

# if __name__ == "__main__":
#     pass
# else:
#     from .spectrum_template import SpecTemplate, SpectrumWindowLimits, SpectrumWindows


class SpectrumMethodException(ValueError):
    pass


class SpectrumMethods:
    """
    Parent class to hold several Spetrum Methods as children
    """

    data = SpecTemplate

    def __init__(self, ramanshift, intensity, label="", **kwargs):
        """


        Parameters
        ----------
        ramanshift : array or list
            collection of the ramanshift values
        intensity : array or list
            collection of the intensity values
        label : TYPE, optional
            DESCRIPTION. The default is "".
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        self.ramanshift = ramanshift
        self.intensity = intensity
        self.label = label
        self.kwargs = kwargs

    @staticmethod
    def filtered_int(intensity=None):

        try:
            int_savgol_fltr = signal.savgol_filter(intensity, 13, 3, mode="nearest")
        except Exception as e:
            raise SpectrumMethodException(f"no intensity given to filter, {e}")
            int_savgol_fltr = []
        return int_savgol_fltr


class SpectrumSplitter(SpectrumMethods):
    """
    For splitting of spectra into the several SpectrumWindows,
    the names of the windows are taken from SpectrumWindows
    and set as attributes to the instance.
    """

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)

    def split_data(self, spec_windows=SpectrumWindows()):
        _r, _int = self.ramanshift, self.intensity
        # self.register.get(on_lbl)
        _d = {}
        for windowname, limits in spec_windows.items():
            ind = (_r >= np.min(limits)) & (_r <= np.max(limits))
            # _intslice = _int[ind]
            label = f"window_{windowname}"
            if self.label:
                label = f"{self.label}_{label}"
            _data = self.data(_r[ind], _int[ind], label)
            setattr(self, label, _data)
            _d.update(**{windowname: _data})
        self.windows_data = _d


# class Filter(SpectrumMethods):
# '''
# For filtering the intensity of a spectrum
# '''

# def get_filtered(self, intensity):


class BaselineSubtractorNormalizer(SpectrumSplitter):
    """
    For baseline subtraction as well as normalization of a spectrum
    """

    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.split_data()
        self.windowlimits = SpectrumWindowLimits()
        self.subtract_loop()
        self.get_normalization_factor()
        self.set_normalized_data()

    def subtract_loop(self):
        _blcorr = {}
        _info = {}
        for windowname, spec in self.windows_data.items():
            blcorr_int, blcorr_lin = self.subtract_baseline_per_window(windowname, spec)
            label = f"blcorr_{windowname}"
            if self.label:
                label = f"{self.label}_{label}"
            _data = self.data(spec.ramanshift, blcorr_int, label)
            _blcorr.update(**{windowname: _data})
            _info.update(**{windowname: blcorr_lin})
        self.blcorr_data = _blcorr
        self.blcorr_info = _info

    def subtract_baseline_per_window(self, windowname, spec):
        rs = spec.ramanshift
        if windowname[0:4] in ("full", "norm"):
            i_fltrd_dspkd_fit = self.windows_data.get("1st_order").intensity
        else:
            i_fltrd_dspkd_fit = spec.intensity
        _limits = self.windowlimits.get(windowname)
        # assert bool(_limits),f'no limits for {windowname}'
        bl_linear = linregress(
            rs[[0, -1]],
            [
                np.mean(i_fltrd_dspkd_fit[0 : _limits[0]]),
                np.mean(i_fltrd_dspkd_fit[_limits[1] : :]),
            ],
        )
        i_blcor = spec.intensity - (bl_linear[0] * rs + bl_linear[1])
        #        blcor = pd.DataFrame({'Raman-shift' : w, 'I_bl_corrected' :i_blcor, 'I_raw_data' : i})
        return i_blcor, bl_linear

    def get_normalization_factor(self, norm_method="simple"):
        if norm_method == "simple":
            normalization_intensity = np.nanmax(
                self.blcorr_data["normalization"].intensity
            )

        if 0:
            # IDEA not implemented
            if norm_method == "fit":
                normalization = NormalizeFit(
                    self.blcorr_data["1st_order"], plotprint=False
                )  # IDEA still implement this NormalizeFit
                normalization_intensity = normalization["IG"]

        self.norm_factor = 1 / normalization_intensity
        norm_dict = {
            "norm_factor": self.norm_factor,
            "norm_method": norm_method,
            "norm_int": normalization_intensity,
        }
        self.norm_dict = norm_dict

    def set_normalized_data(self):
        _normd = {}
        for windowname, spec in self.blcorr_data.items():

            label = f"norm_blcorr_{windowname}"
            if self.label:
                label = f"{self.label}_{label}"

            _data = self.data(spec.ramanshift, spec.intensity * self.norm_factor, label)
            _normd.update(**{windowname: _data})
        self.norm_data = _normd


def NormalizeFit(spec, plotprint=False):
    pass  # IDEA placeholder


def array_nan_checker(array):
    _nans = [n for n, i in enumerate(array) if np.isnan(i)]
    return _nans


class Despiker(SpectrumMethods):
    """
    A Despiking algorithm from reference literature: https://doi.org/10.1016/j.chemolab.2018.06.009

    Parameters
    ----------
    input_intensity : np.ndarray
        The intensity array of which the desipked intensity will be calculated.
    info : dict, optional
        Extra information for despiking settings are added to this dict.
    Attributes
    ---------
    despiked_intensity : np.ndarray
        The resulting array of the despiked intensity of same length as input_intensity.
    Notes
    --------
    Let Y1;...;Yn represent the values of a single Raman spectrum recorded at equally spaced wavenumbers.
    From this series, form the detrended differenced seriesr Yt ...:This simple
    ata processing step has the effect of annihilating linear and slow movingcurve linear trends, however,
    sharp localised spikes will be preserved.Denote the median and the median absolute deviation of
    D.A. Whitaker, K. Hayes. Chemometrics and Intelligent Laboratory Systems 179 (2018) 82–84
    """

    keys = ["input_intensity", "Zt", "Z_t_filtered", "despiked_intensity"]

    def __init__(
        self, intensity: np.array([]), Z_threshold=4, moving_window_size=1, info={}
    ):
        self.info = info
        self.Z_threshold = Z_threshold
        self.moving_window_size = moving_window_size

        self.info.update(
            {"Z_threshold": Z_threshold, "Z_filter_ma": moving_window_size}
        )

        # these get populated by the run_despike call in the setter
        self.result = {}
        self.df = pd.DataFrame()

        # setter calls to run_despike
        self._int = intensity

        # _new_int = copy.deepcopy(intensity)
        self.input_intensity = intensity

    @property
    def input_intensity(self):
        return self._input_intensity

    @input_intensity.setter
    def input_intensity(self, value):
        """sanitizes the input argument value for an array"""

        type_test = str(type(value))
        if "__main__" in type_test:
            if "intensity" in value._fields:
                val_intensity = value.intensity
        elif "numpy.ndarray" in type_test:
            val_intensity = value
        elif "dict" in type_test:
            val_intensity = value.get([i for i in value.keys() if "intensity" in i][0])
        else:
            raise ValueError(f"Despike input error {type_test} for {value}")

        self.info.update({"input_type": type_test})
        self._input_intensity = val_intensity
        self.despiked_intensity = val_intensity

    @property
    def despiked_intensity(self):
        return self._despiked_intensity

    @despiked_intensity.setter
    def despiked_intensity(self, value):

        result = self.run_despike_steps(value, self.Z_threshold)

        self._despiked_intensity = result["despiked_intensity"]

        self.result = result
        self.df = pd.DataFrame(result)

    def run_despike_steps(self, intensity, Z_threshold):

        Z_t = self.calc_Z(intensity)
        Z_t_filtered = self.calc_Z_filtered(Z_t, Z_threshold)
        i_despiked = self.despike_filter(
            intensity, Z_t_filtered, self.moving_window_size
        )

        result_values = [intensity, Z_t, Z_t_filtered, i_despiked]
        result = dict(zip(self.keys, result_values))
        return result

    @staticmethod
    def calc_Z(intensity):
        dYt = np.append(np.diff(intensity), 0)
        #    dYt = intensity.diff()
        dYt_Median = np.median(dYt)
        #    M = dYt.median()
        #    dYt_M =  dYt-M
        dYt_MAD = np.median(abs(dYt - dYt_Median))
        #    MAD = np.mad(dYt)
        Z_t = (0.6745 * (dYt - dYt_Median)) / dYt_MAD
        #    intensity = blcor.assign(**{'abs_Z_t': Z_t.abs()})
        return Z_t

    @staticmethod
    def calc_Z_filtered(Z_t, Z_threshold):
        Z_t_filtered = copy.deepcopy(Z_t)
        Z_t_filtered[np.abs(Z_t) > Z_threshold] = np.nan
        Z_t_filtered[0] = Z_t_filtered[-1] = 0
        return Z_t_filtered
        # self.Z_t_filtered = Z_t_filtered

    #        Z_threshold = 3.5
    #        Z_t_filtered = [Z_t
    #        Z_t_filtered[Z_filter_indx] = np.nan
    #        y_out,n = intensity,len(intensity)
    @staticmethod
    def despike_filter(
        intensity, Z_t_filtered, moving_window_size, ignore_lims=(20, 46)
    ):
        n = len(intensity)
        i_despiked = copy.deepcopy(intensity)
        spikes = np.where(np.isnan(Z_t_filtered))
        for i in list(spikes[0]):

            if i < ignore_lims[0] or i > ignore_lims[1]:
                w = np.arange(
                    max(0, i - moving_window_size), min(n, i + moving_window_size)
                )
                w = w[~np.isnan(Z_t_filtered[w])]
                if intensity[w].any():
                    i_despiked[i] = np.mean(intensity[w])
                else:
                    i_despiked[i] = intensity[i]
            # else:
            # pass  # ignored
        return i_despiked

    def plot_Z(self):
        # fig,ax = plt.subplots(2)
        self.df.plot(y=["Zt", "Z_t_filtered"], alpha=0.5)
        self.df.plot(y=["input_intensity", "despiked_intensity"], alpha=0.8)
        # plt.show()
        # plt.close()
