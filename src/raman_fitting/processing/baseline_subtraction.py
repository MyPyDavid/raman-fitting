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
    i_blcor = spec.intensity - (bl_linear[0] * spec.ramanshift + bl_linear[1])

    return i_blcor, bl_linear


def subtract_baseline_from_split_spectrum(
    split_spectrum: SplitSpectrum, label=None
) -> SplitSpectrum:
    if split_spectrum.split_spectra is None:
        raise ValueError("Missing regions of split spectrum.")

    spec_blcorr_regions: list[SpectrumData] = []
    _info: dict = {}
    label = "blcorr" if label is None else label
    for region_name, spec in split_spectrum:
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
            **{
                "ramanshift": spec.ramanshift,
                "intensity": blcorr_int,
                "label": new_label,
                "region_name": region_name,
                "source": spec.source,
                "processing_steps": spec.processing_steps.copy(),
            }
        )
        spec_blcorr.add_processing_step(f"baseline subtracted with {label}")

        spec_blcorr_regions.append(spec_blcorr)
        _info.update(**{region_name: blcorr_lin})

    return split_spectrum.model_copy(
        update={"spec_regions": spec_blcorr_regions, "info": _info}
    )
