"""
Created on Mon May  3 11:10:59 2021

@author: dw
"""

from typing import Dict, Tuple, Any
import copy
import logging

import numpy as np

from pydantic import BaseModel, Field, computed_field

from raman_fitting.models.spectrum import SpectrumData

logger = logging.getLogger(__name__)


class SpectrumDespiker(BaseModel):
    spectrum: SpectrumData
    threshold_z_value: int = 4
    moving_region_size: int = 1
    ignore_lims: Tuple[int, int] = (20, 46)
    info: Dict = Field(default_factory=dict)

    @computed_field
    @property
    def despiked_spectrum(self) -> SpectrumData:
        despiked_intensity, result_info = self.run_despiking_algorithm(
            self.spectrum.intensity
        )
        # Create a new instance of SpectrumData with the updated intensity
        despiked_spec = SpectrumData(
            ramanshift=self.spectrum.ramanshift,
            intensity=despiked_intensity,
            label=self.spectrum.label,
            source=self.spectrum.source,
            region_name=self.spectrum.region_name,
            processing_steps=self.spectrum.processing_steps.copy(),
        )
        despiked_spec.add_processing_step(f"Despiked: {self.__class__.__name__}")
        self.info.update(**result_info)
        return despiked_spec

    def run_despiking_algorithm(self, intensity: np.ndarray) -> Tuple[np.ndarray, Dict]:
        despiked_intensity, result_info = despike_spectrum_intensity(
            intensity,
            self.threshold_z_value,
            self.moving_region_size,
            ignore_lims=self.ignore_lims,
        )
        return despiked_intensity, result_info


def despike_spectrum_intensity(
    intensity: np.ndarray,
    threshold_z_value: int,
    moving_region_size: int,
    ignore_lims=(20, 46),
) -> Tuple[np.ndarray, Dict[str, Any]]:
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

    z_intensity = calc_z_value_intensity(intensity)
    filtered_z_intensity = filter_z_intensity_values(z_intensity, threshold_z_value)
    i_despiked = despike_filter(
        intensity, filtered_z_intensity, moving_region_size, ignore_lims=ignore_lims
    )
    result = {"z_intensity": z_intensity, "filtered_z_intensity": filtered_z_intensity}
    return i_despiked, result


def calc_z_value_intensity(intensity: np.ndarray) -> np.ndarray:
    diff_intensity = np.append(np.diff(intensity), 0)  # dYt
    median_diff_intensity = np.median(diff_intensity)  # dYt_Median
    median_abs_deviation = np.median(abs(diff_intensity - median_diff_intensity))

    # Handle the case where median_abs_deviation is zero
    if median_abs_deviation == 0:
        logger.warning(
            "median_abs_deviation is zero, setting intensity_values_z to zero."
        )
        return np.zeros_like(diff_intensity)

    intensity_values_z = (
        0.6745 * (diff_intensity - median_diff_intensity)
    ) / median_abs_deviation
    return intensity_values_z


def filter_z_intensity_values(z_intensity, z_intensitythreshold):
    filtered_z_intensity = z_intensity.astype(float)
    filtered_z_intensity[np.abs(z_intensity) > z_intensitythreshold] = np.nan
    filtered_z_intensity[0] = filtered_z_intensity[-1] = 0
    return filtered_z_intensity


def despike_filter(
    intensity: np.ndarray,
    filtered_z_intensity: np.ndarray,
    moving_region_size: int,
    ignore_lims=(20, 46),
):
    n = len(intensity)
    i_despiked = copy.deepcopy(intensity)
    spikes = np.nonzero(np.isnan(filtered_z_intensity))
    for i in list(spikes[0]):
        if i < ignore_lims[0] or i > ignore_lims[1]:
            w = np.arange(
                max(0, i - moving_region_size), min(n, i + moving_region_size)
            )
            w = w[~np.isnan(filtered_z_intensity[w])]
            if intensity[w].any():
                i_despiked[i] = np.mean(intensity[w])
            else:
                i_despiked[i] = intensity[i]
    return i_despiked


def despike_spectrum_data(spectrum: SpectrumData) -> SpectrumData:
    return SpectrumDespiker(spectrum=spectrum).despiked_spectrum
