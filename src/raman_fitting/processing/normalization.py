import logging
from typing import Optional

import numpy as np

from ..models.splitter import SplittedSpectrum
from ..models.spectrum import SpectrumData

logger = logging.getLogger(__name__)


def get_simple_normalization_intensity(splitted_spectrum: SplittedSpectrum) -> float:
    window_keys = splitted_spectrum.spec_windows.keys()
    if not any("normalization" in i for i in window_keys):
        raise ValueError("Missing normalization key")

    norm_window_name = list(filter(lambda x: "normalization" in x, window_keys))[0]

    norm_spec = splitted_spectrum.spec_windows[norm_window_name]
    normalization_intensity = np.nanmax(norm_spec.intensity)
    return normalization_intensity


def get_normalization_factor(
    splitted_spectrum: SplittedSpectrum, norm_method="simple"
) -> float:
    try:
        if norm_method == "simple":
            normalization_intensity = get_simple_normalization_intensity(
                splitted_spectrum
            )
        elif norm_method == "fit":
            raise NotImplementedError("NormalizeFit not yet implemented")
            # IDEA not implemented
            # normalization = NormalizeFit(
            #     self.blcorr_data["first_order"], plotprint=False
            # )  # IDEA still implement this NormalizeFit
            # normalization_intensity = normalization["IG"]
        else:
            logger.warning(f"unknown normalization method {norm_method}")
            normalization_intensity = 1
    except Exception as exc:
        logger.error(f"normalization error {exc}")
        normalization_intensity = 1
        raise exc from exc
    norm_factor = 1 / normalization_intensity
    return norm_factor


def normalize_windows_in_splitted_spectrum(
    splitted_spectrum: SplittedSpectrum, norm_factor: float, label: Optional[str] = None
) -> SplittedSpectrum:
    norm_spec_windows = {}
    norm_infos = {}
    label = splitted_spectrum.spectrum.label if label is None else label
    for window_name, spec in splitted_spectrum.spec_windows.items():
        norm_label = f"{window_name}_{label}" if window_name not in label else label
        norm_label = f"norm_{norm_label}" if "norm" not in norm_label else norm_label
        # label looks like "norm_windowname_label"
        _data = SpectrumData(
            **{
                "ramanshift": spec.ramanshift,
                "intensity": spec.intensity * norm_factor,
                "label": norm_label,
                "window_name": window_name,
            }
        )
        norm_spec_windows.update(**{window_name: _data})
        norm_infos.update(**{window_name: {"normalization_factor": norm_factor}})
    norm_spectra = splitted_spectrum.model_copy(
        update={"spec_windows": norm_spec_windows, "info": norm_infos}
    )
    return norm_spectra


def normalize_splitted_spectrum(
    splitted_spectrum: SplittedSpectrum,
) -> SplittedSpectrum:
    "Normalize the spectrum intensity according to normalization method."
    normalization_factor = get_normalization_factor(splitted_spectrum)
    norm_data = normalize_windows_in_splitted_spectrum(
        splitted_spectrum, normalization_factor
    )
    return norm_data
