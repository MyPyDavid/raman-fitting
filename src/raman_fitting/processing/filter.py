#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
from scipy import signal

from raman_fitting.processing.spectrum_template import (
    SpecTemplate,
)


class SpectrumMethodException(ValueError):
    pass


@staticmethod
def savgol_filter(intensity=None, **kwargs):
    if intensity is None:
        raise ValueError("no intensity given to filter")
    int_savgol_fltr = signal.savgol_filter(intensity, 13, 3, mode="nearest")
    return int_savgol_fltr


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
        return savgol_filter(intensity=intensity)


def NormalizeFit(spec, plotprint=False):
    pass  # IDEA placeholder


def array_nan_checker(array):
    _nans = [n for n, i in enumerate(array) if np.isnan(i)]
    return _nans
