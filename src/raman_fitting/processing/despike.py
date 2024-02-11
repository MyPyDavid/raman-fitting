"""
Created on Mon May  3 11:10:59 2021

@author: dw
"""

from typing import Dict, Tuple, Any
import copy
import logging

import numpy as np

from pydantic import BaseModel, Field, model_validator

from raman_fitting.models.spectrum import SpectrumData

logger = logging.getLogger(__name__)


class SpectrumDespiker(BaseModel):
    spectrum: SpectrumData = None
    Z_threshold: int = 4
    moving_window_size: int = 1
    ignore_lims: Tuple[int, int] = (20, 46)
    info: Dict = Field(default_factory=dict)
    despiked_spectrum: SpectrumData = Field(None)

    @model_validator(mode="after")
    def process_spectrum(self) -> "SpectrumDespiker":
        if self.spectrum is None:
            raise ValueError("SpectrumDespiker, spectrum is None")
        despiked_intensity, result_info = self.call_despike_spectrum(
            self.spectrum.intensity
        )
        despiked_spec = self.spectrum.model_copy(
            update={"intensity": despiked_intensity}, deep=True
        )
        SpectrumData.model_validate(despiked_spec, from_attributes=True)
        self.despiked_spectrum = despiked_spec
        self.info.update(**result_info)
        return self

    def process_intensity(self, intensity: np.ndarray) -> np.ndarray:
        despiked_intensity, _ = self.call_despike_spectrum(intensity)
        return despiked_intensity

    def call_despike_spectrum(self, intensity: np.ndarray) -> Tuple[np.ndarray, Dict]:
        despiked_intensity, result_info = despike_spectrum(
            intensity,
            self.Z_threshold,
            self.moving_window_size,
            ignore_lims=self.ignore_lims,
        )
        return despiked_intensity, result_info


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
        self, intensity: np.ndarray([]), Z_threshold=4, moving_window_size=1, info={}
    ):
        self.info = info
        self.Z_threshold = Z_threshold
        self.moving_window_size = moving_window_size

        self.info.update(
            {"Z_threshold": Z_threshold, "Z_filter_ma": moving_window_size}
        )

        # these get populated by the run_despike call in the setter
        self.result = {}

        # setter calls to run_despike
        self._int = intensity

        # _new_int = copy.deepcopy(intensity)
        self.input_intensity = intensity


def despike_spectrum(
    intensity: np.ndarray,
    Z_threshold: int,
    moving_window_size: int,
    ignore_lims=(20, 46),
) -> Tuple[np.ndarray, Dict[str, Any]]:
    Z_t = calc_Z(intensity)
    Z_t_filtered = calc_Z_filtered(Z_t, Z_threshold)
    i_despiked = despike_filter(
        intensity, Z_t_filtered, moving_window_size, ignore_lims=ignore_lims
    )
    result = {"Z_t": Z_t, "Z_t_filtered": Z_t_filtered}
    return i_despiked, result


def calc_Z(intensity: np.ndarray) -> np.ndarray:
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


def calc_Z_filtered(Z_t, Z_threshold):
    Z_t_filtered = copy.deepcopy(Z_t)
    Z_t_filtered[np.abs(Z_t) > Z_threshold] = np.nan
    Z_t_filtered[0] = Z_t_filtered[-1] = 0
    return Z_t_filtered


def despike_filter(
    intensity: np.ndarray,
    Z_t_filtered: np.ndarray,
    moving_window_size: int,
    ignore_lims=(20, 46),
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
