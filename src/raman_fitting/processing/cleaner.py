#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy

import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import linregress

# from collections import namedtuple


if __name__ == "__main__":
    from spectrum_template import SpecTemplate, SpectrumWindowLimits, SpectrumWindows

    # pass
else:
    from .spectrum_template import SpecTemplate, SpectrumWindowLimits, SpectrumWindows


class SpectrumMethodException(ValueError):
    pass


class SpectrumMethods:
    """
    Parent class to hold several Spetrum Methods as children
    """

    data = SpecTemplate

    def __init__(self, ramanshift, intensity, label="", **kwargs):
        self.ramanshift = ramanshift
        self.intensity = intensity
        self.label = label
        self.kwargs = kwargs

    @staticmethod
    def filtered_int(intensity=None):
        # if hasattr(self, 'intensity') and intensity == None:
        # _int = self.intensity
        if len(intensity) > 0:
            _int = intensity
        else:
            raise SpectrumMethodException("no intensity given to filter")
        int_savgol_fltr = signal.savgol_filter(intensity, 13, 3, mode="nearest")
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

        elif norm_method == "fit":
            normalization = NormalizeFit(
                self.blcorr_data["1st_order"], plotprint=False
            )  # TODO still implement this NormalizeFit
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
    pass  # TODO placeholder


def array_nan_checker(array):
    _nans = [n for n, i in enumerate(array) if np.isnan(i)]
    return _nans


class Despiker(SpectrumMethods):
    """
    A Despiking algorithm from reference literature: https://doi.org/10.1016/j.chemolab.2018.06.009.

    Parameters
    ----------
    input_intensity : np.ndarray
        The intensity array of which the desipked intensity will be calculated.
    info : dict, optional
        Extra information from despiking settings are added to this dict.
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

    def __init__(self, input_intensity, Z_threshold=20, info={}):
        self.info = info
        self.Z_threshold = Z_threshold
        self.input_intensity = copy.deepcopy(input_intensity)
        # self.check_input_intensity()

    @property
    def input_intensity(self):
        return self._input_intensity

    @input_intensity.setter
    def input_intensity(self, value):

        type_test = str(type(value))
        if "__main__" in type_test:
            if "intensity" in value._fields:
                int_used = value.intensity
        elif "numpy.ndarray" in type_test:
            int_used = value
        elif "dict" in type_test:
            int_used = value.get([i for i in value.keys() if "intensity" in i][0])
        else:
            raise ValueError(f"Despike input error {type_test} for {value}")

        self.info.update({"input_type": type_test})
        self._input_intensity = int_used
        self.run_despike()

    def run_despike(self):
        self.calc_Z()
        self.calc_Z_filtered()
        self.apply_despike_filter()
        self.pack_to_df()

    def calc_Z(self):
        intensity = self.input_intensity
        dYt = np.append(np.diff(intensity), 0)
        #    dYt = intensity.diff()
        dYt_Median = np.median(dYt)
        #    M = dYt.median()
        #    dYt_M =  dYt-M
        dYt_MAD = np.median(abs(dYt - dYt_Median))
        #    MAD = np.mad(dYt)
        Z_t = (0.6745 * (dYt - dYt_Median)) / dYt_MAD
        #    intensity = blcor.assign(**{'abs_Z_t': Z_t.abs()})
        self.Z_t = Z_t

    def calc_Z_filtered(self):
        Z_t_filtered = copy.deepcopy(self.Z_t)
        Z_t_filtered[np.abs(self.Z_t) > self.Z_threshold] = np.nan
        Z_t_filtered[0] = Z_t_filtered[-1] = 0
        self.Z_t_filtered = Z_t_filtered
        self.info.update({"Z_threshold": self.Z_threshold})

    #        Z_threshold = 3.5
    #        Z_t_filtered = [Z_t
    #        Z_t_filtered[Z_filter_indx] = np.nan
    #        y_out,n = intensity,len(intensity)

    def apply_despike_filter(self, ma=5, ignore_lims=(20, 46)):
        intensity, Z_t_filtered = copy.deepcopy(self.input_intensity), self.Z_t_filtered
        n = len(intensity)
        i_despiked = intensity
        spikes = np.where(np.isnan(Z_t_filtered))
        for i in list(spikes[0]):

            if i < ignore_lims[0] or i > ignore_lims[1]:
                w = np.arange(max(1, i - ma), min(n, i + ma))
                w = w[~np.isnan(Z_t_filtered[w])]
                i_despiked[i] = np.mean(intensity[w])
            else:
                pass  # ignored
        self.info.update({"Z_filter_ma": ma})
        self.despiked_intensity = i_despiked

    def pack_to_df(self):
        cols = [
            self.input_intensity,
            self.Z_t,
            self.Z_t_filtered,
            self.despiked_intensity,
        ]
        names = ["input_intensity", "Zt", "Z_t_filtered", "despiked_intensity"]
        _d = dict(zip(names, cols))
        self.dict = _d
        self.df = pd.DataFrame(_d)

    def plot_Z(self):
        # fig,ax = plt.subplots(2)
        self.df.plot(y=["Zt", "Z_t_filtered"], alpha=0.5)
        self.df.plot(y=["input_intensity", "despiked_intensity"], alpha=0.5)
        # plt.show()
        # plt.close()
