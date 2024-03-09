from typing import Optional

import numpy as np

from ..models.splitter import SplittedSpectrum
from ..models.spectrum import SpectrumData
from ..models.fit_models import SpectrumFitModel, LMFitModel

from loguru import logger


def get_simple_normalization_intensity(splitted_spectrum: SplittedSpectrum) -> float:
    norm_spec = splitted_spectrum.get_window("normalization")
    normalization_intensity = np.nanmax(norm_spec.intensity)
    return normalization_intensity


def get_normalization_factor(
    splitted_spectrum: SplittedSpectrum,
    norm_method="simple",
    normalization_model: LMFitModel = None,
) -> float:
    simple_norm = get_simple_normalization_intensity(splitted_spectrum)
    normalization_intensity = simple_norm

    if "fit" in norm_method and normalization_model is not None:
        fit_norm = normalizer_fit_model(
            splitted_spectrum, normalization_model=normalization_model
        )
        if fit_norm is not None:
            normalization_intensity = fit_norm
    norm_factor = 1 / normalization_intensity

    return norm_factor


def normalize_regions_in_splitted_spectrum(
    splitted_spectrum: SplittedSpectrum, norm_factor: float, label: Optional[str] = None
) -> SplittedSpectrum:
    norm_spec_regions = {}
    norm_infos = {}
    label = splitted_spectrum.spectrum.label if label is None else label
    for window_name, spec in splitted_spectrum.spec_regions.items():
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
        norm_spec_regions.update(**{window_name: _data})
        norm_infos.update(**{window_name: {"normalization_factor": norm_factor}})
    norm_spectra = splitted_spectrum.model_copy(
        update={"spec_regions": norm_spec_regions, "info": norm_infos}
    )
    return norm_spectra


def normalize_splitted_spectrum(
    splitted_spectrum: SplittedSpectrum,
) -> SplittedSpectrum:
    "Normalize the spectrum intensity according to normalization method."
    normalization_factor = get_normalization_factor(splitted_spectrum)
    norm_data = normalize_regions_in_splitted_spectrum(
        splitted_spectrum, normalization_factor
    )
    return norm_data


def normalizer_fit_model(
    specrum: SpectrumData, normalization_model: LMFitModel
) -> float | None:
    spec_fit = SpectrumFitModel(spectrum=specrum, model=normalization_model)
    spec_fit.run_fit()
    if not spec_fit.fit_result:
        return
    try:
        return spec_fit.fit_result.params["G_height"].value
    except KeyError as e:
        logger.error(e)
    except Exception as e:
        raise e from e
