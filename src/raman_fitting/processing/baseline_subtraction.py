import numpy as np
from scipy.stats import linregress

from ..models.deconvolution.spectrum_regions import SpectrumRegionsLimitsSet
from ..models.splitter import SplitSpectrum
from ..models.spectrum import SpectrumData

from loguru import logger


def subtract_baseline_per_region(
    spec: SpectrumData,
    split_spectrum: SplitSpectrum,
    region_limits: SpectrumRegionsLimitsSet,
):
    if (  # override the selected region with first order for full and norm
        any((i in spec.region_name or i in spec.label) for i in ("full", "norm"))
    ):
        selected_intensity = split_spectrum.get_spec_for_region("first_order").intensity
        region_config = region_limits["first_order"]
    else:
        selected_intensity = spec.intensity
        region_config = region_limits[spec.region_name]

    bl_linear = linregress(
        spec.ramanshift[[0, -1]],
        [
            np.mean(selected_intensity[0 : region_config.extra_margin]),
            np.mean(selected_intensity[-region_config.extra_margin : :]),
        ],
    )
    i_blcorr = spec.intensity - (bl_linear[0] * spec.ramanshift + bl_linear[1])

    return i_blcorr, bl_linear


def subtract_baseline_from_split_spectrum(
    split_spectrum: SplitSpectrum, label=None
) -> SplitSpectrum:
    if split_spectrum.computed_split_spectra_from_spectrum is None:
        raise ValueError("Missing regions of split spectrum.")

    spec_blcorr_regions: list[SpectrumData] = []
    blcorr_info: dict = {}
    label = "blcorr" if label is None else label
    for region_name, spec in split_spectrum:
        if not len(spec):
            continue

        blcorr_int, blcorr_lin = subtract_baseline_per_region(
            spec, split_spectrum, split_spectrum.region_limits
        )
        if any(np.isnan(i) for i in blcorr_int):
            logger.warning(
                f"Subtract baseline failed for {region_name} because of nan."
            )
            continue

        new_label = f"{label}_{spec.label}" if label not in spec.label else spec.label

        spec_blcorr = SpectrumData(
            ramanshift=spec.ramanshift,
            intensity=blcorr_int,
            label=new_label,
            source=spec.source,
            region_name=spec.region_name,
            processing_steps=spec.processing_steps.copy(),
        )
        spec_blcorr.add_processing_step(
            f"baseline subtracted with {label}, {blcorr_lin}"
        )
        spec_blcorr_regions.append(spec_blcorr)
        blcorr_info.update(**{region_name: blcorr_lin})

    new_split_spectrum = SplitSpectrum(
        spectrum=split_spectrum.spectrum,
        region_limits=split_spectrum.region_limits,
        split_spectra=spec_blcorr_regions,
        info=blcorr_info,
    )
    return new_split_spectrum
