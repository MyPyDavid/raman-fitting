import logging

import numpy as np
from scipy.stats import linregress

from ..models.splitter import SplittedSpectrum
from ..models.spectrum import SpectrumData

logger = logging.getLogger(__name__)


def subtract_baseline_per_window(
    spec: SpectrumData, splitted_spectrum: SplittedSpectrum
):
    ramanshift = spec.ramanshift
    intensity = spec.intensity
    window_name = spec.window_name
    label = spec.label
    regions_data = splitted_spectrum.spec_regions
    window_limits = splitted_spectrum.window_limits
    selected_intensity = intensity
    window_config = window_limits[window_name]
    window_name_first_order = list(
        filter(lambda x: "first_order" in x, regions_data.keys())
    )
    if (
        any((i in window_name or i in label) for i in ("full", "norm"))
        and window_name_first_order
    ):
        selected_intensity = regions_data[window_name_first_order[0]].intensity
        window_config = window_limits["first_order"]

    bl_linear = linregress(
        ramanshift[[0, -1]],
        [
            np.mean(selected_intensity[0 : window_config.extra_margin]),
            np.mean(selected_intensity[-window_config.extra_margin : :]),
        ],
    )
    i_blcor = intensity - (bl_linear[0] * ramanshift + bl_linear[1])
    # if np.isnan(i_blcor).any():
    #     raise ValueError("There are nan values in subtract_baseline_per_window")
    return i_blcor, bl_linear


def subtract_baseline_from_splitted_spectrum(
    splitted_spectrum: SplittedSpectrum, label=None
) -> SplittedSpectrum:
    _bl_spec_regions = {}
    _info = {}
    label = "blcorr" if label is None else label
    for window_name, spec in splitted_spectrum.spec_regions.items():
        blcorr_int, blcorr_lin = subtract_baseline_per_window(spec, splitted_spectrum)
        new_label = f"{label}_{spec.label}" if label not in spec.label else spec.label
        spec = SpectrumData(
            **{
                "ramanshift": spec.ramanshift,
                "intensity": blcorr_int,
                "label": new_label,
                "windown_name": window_name,
            }
        )
        _bl_spec_regions.update(**{window_name: spec})
        _info.update(**{window_name: blcorr_lin})
    bl_corrected_spectra = splitted_spectrum.model_copy(
        update={"spec_regions": _bl_spec_regions, "info": _info}
    )
    return bl_corrected_spectra


def subtract_baseline(
    ramanshift: np.array, intensity: np.array, label: str = None
) -> SplittedSpectrum:
    "Subtract the a baseline of background intensity of a spectrum."
    spectrum = SpectrumData(ramanshift=ramanshift, intensity=intensity, label=label)
    splitted_spectrum = SplittedSpectrum(spectrum=spectrum)
    blcorrected_spectrum = subtract_baseline_from_splitted_spectrum(
        splitted_spectrum, label=label
    )
    return blcorrected_spectrum
