from typing import Optional

import numpy as np

from ..models.splitter import SplitSpectrum
from ..models.spectrum import SpectrumData
from ..models.fit_models import SpectrumFitModel, LMFitModel

from loguru import logger


def get_simple_normalization_intensity(split_spectrum: SplitSpectrum) -> float:
    try:
        return np.nanmax(split_spectrum.get_spec_for_region("normalization").intensity)
    except ValueError:
        valid_regions = [spec for _n, spec in split_spectrum if spec.intensity.any()]
        return max([i.intensity.max() for i in valid_regions])


def get_normalization_factor(
    split_spectrum: SplitSpectrum,
    norm_method="simple",
    normalization_model: LMFitModel = None,
) -> float:
    simple_norm_factor = get_simple_normalization_intensity(split_spectrum)
    normalization_intensity = simple_norm_factor

    if "fit" in norm_method and normalization_model is not None:
        fit_norm = normalizer_fit_model(
            split_spectrum.get_spec_for_region("normalization"),
            normalization_model=normalization_model,
        )
        if fit_norm is not None:
            normalization_intensity = fit_norm
    norm_factor = 1 / normalization_intensity

    return norm_factor


def normalize_regions_in_split_spectrum(
    split_spectrum: SplitSpectrum, norm_factor: float, label: Optional[str] = None
) -> SplitSpectrum:
    norm_spec_regions = []
    norm_infos = {}
    label = split_spectrum.spectrum.label if label is None else label
    for region_name, spec in split_spectrum:
        norm_label = f"{region_name}_{label}" if region_name not in label else label
        norm_label = f"norm_{norm_label}" if "norm" not in norm_label else norm_label
        # label looks like "norm_regionname_label"

        new_spec_region = SpectrumData(
            ramanshift=spec.ramanshift,
            intensity=spec.intensity * norm_factor,
            label=norm_label,
            source=spec.source,
            region=spec.region,
            processing_steps=spec.processing_steps.copy(),
        )
        new_spec_region.add_processing_step(f"normalization with {norm_factor}")
        norm_spec_regions.append(new_spec_region)
        norm_infos.update(**{region_name: {"normalization_factor": norm_factor}})

    new_split_spectrum = SplitSpectrum(
        spectrum=split_spectrum.spectrum,
        region_limits=split_spectrum.region_limits,
        split_spectra=norm_spec_regions,
        info=norm_infos,
    )
    return new_split_spectrum


def normalize_split_spectrum(
    split_spectrum: SplitSpectrum,
) -> SplitSpectrum:
    """Normalize the spectrum intensity according to normalization method."""
    return normalize_regions_in_split_spectrum(
        split_spectrum, get_normalization_factor(split_spectrum)
    )


def normalizer_fit_model(
    spectrum: SpectrumData, normalization_model: LMFitModel
) -> float | None:
    spec_fit = SpectrumFitModel(spectrum=spectrum, model=normalization_model)
    spec_fit.run()
    if not spec_fit.fit_result:
        return
    try:
        return spec_fit.fit_result.params["G_height"].value
    except KeyError as e:
        logger.error(e)
