#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 11:10:59 2021

@author: dw
"""

import copy
import logging

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class Despiker:
    """
    A Despiking algorithm from reference literature:
      https://doi.org/10.1016/j.chemolab.2018.06.009

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
    Let Y1;...;Yn represent the values of a single Raman spectrum recorded at
    equally spaced wavenumbers.
    From this series, form the detrended differenced seriesr Yt ...:This simple
    data processing step has the effect of annihilating linear and slow movingcurve
    linear trends, however,
    sharp localised spikes will be preserved.Denote the median and the median absolute
    deviation of
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
        return i_despiked

    def plot_Z(self):
        # fig,ax = plt.subplots(2)
        self.df.plot(y=["Zt", "Z_t_filtered"], alpha=0.5)
        self.df.plot(y=["input_intensity", "despiked_intensity"], alpha=0.8)
        # plt.show()
        # plt.close()
