import logging

import numpy as np
from scipy.stats import linregress

from ..models.splitter import SplitSpectrum
from ..models.spectrum import SpectrumData

logger = logging.getLogger(__name__)


def subtract_baseline_per_region(spec: SpectrumData, split_spectrum: SplitSpectrum):
    ramanshift = spec.ramanshift
    intensity = spec.intensity
    region_name = spec.region_name
    label = spec.label
    regions_data = split_spectrum.spec_regions
    region_limits = split_spectrum.region_limits
    selected_intensity = intensity
    region_config = region_limits[region_name]
    region_name_first_order = list(
        filter(lambda x: "first_order" in x, regions_data.keys())
    )
    if (
        any((i in region_name or i in label) for i in ("full", "norm"))
        and region_name_first_order
    ):
        selected_intensity = regions_data[region_name_first_order[0]].intensity
        region_config = region_limits["first_order"]

    bl_linear = linregress(
        ramanshift[[0, -1]],
        [
            np.mean(selected_intensity[0 : region_config.extra_margin]),
            np.mean(selected_intensity[-region_config.extra_margin : :]),
        ],
    )
    i_blcor = intensity - (bl_linear[0] * ramanshift + bl_linear[1])
    return i_blcor, bl_linear


def subtract_baseline_from_split_spectrum(
    split_spectrum: SplitSpectrum = None, label=None
) -> SplitSpectrum:
    _bl_spec_regions = {}
    _info = {}
    label = "blcorr" if label is None else label
    for region_name, spec in split_spectrum.spec_regions.items():
        blcorr_int, blcorr_lin = subtract_baseline_per_region(spec, split_spectrum)
        new_label = f"{label}_{spec.label}" if label not in spec.label else spec.label
        spec = SpectrumData(
            **{
                "ramanshift": spec.ramanshift,
                "intensity": blcorr_int,
                "label": new_label,
                "region_name": region_name,
                "source": spec.source,
            }
        )
        _bl_spec_regions.update(**{region_name: spec})
        _info.update(**{region_name: blcorr_lin})
    bl_corrected_spectra = split_spectrum.model_copy(
        update={"spec_regions": _bl_spec_regions, "info": _info}
    )
    return bl_corrected_spectra
