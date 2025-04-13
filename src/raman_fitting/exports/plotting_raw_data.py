#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:49:50 2020

@author: DW
"""

from typing import Dict


import matplotlib
import matplotlib.pyplot as plt

from raman_fitting.exports.plot_formatting import get_plot_region_axes
from raman_fitting.models.deconvolution.spectrum_regions import (
    SpectrumRegionsLimitsSet,
)
from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.models.splitter import RegionNames
from raman_fitting.config import settings
from raman_fitting.config.path_settings import (
    ExportPathSettings,
)
from raman_fitting.delegators.models import AggregatedSampleSpectrumFitResult

from loguru import logger

from .models import ExportResult
from .plot_formatting import RAW_MEAN_SPEC_FMT, RAW_SOURCES_SPEC_FMT

matplotlib.rcParams.update({"font.size": 14})

EXCLUDE_REGIONS_RAW_DATA_PLOT = ["low_first_order"]


def filter_regions_for_spectrum(
    regions: SpectrumRegionsLimitsSet, spectrum: SpectrumData
) -> SpectrumRegionsLimitsSet:
    valid_regions = []
    for region in regions:
        if spectrum.ramanshift.min() > region.min:
            continue
        if spectrum.ramanshift.max() < region.max:
            continue
        if region.name in EXCLUDE_REGIONS_RAW_DATA_PLOT:
            continue
        valid_regions.append(region)

    return SpectrumRegionsLimitsSet(regions=valid_regions)


def plot_spectrum(
    ax,
    spec_region,
    spec_source,
    region_name,
    aggregated_spectra,
    valid_regions,
    plot_region_axes,
) -> None:
    if region_name not in valid_regions or region_name not in plot_region_axes:
        return

    ax_ = ax[*plot_region_axes[region_name]]
    ax_.plot(
        spec_region.ramanshift,
        spec_region.intensity,
        label=f"{spec_source.file_info.file.stem}",
        **RAW_SOURCES_SPEC_FMT,
    )
    ax_.set_title(region_name)

    if region_name in aggregated_spectra:
        mean_spec = aggregated_spectra[region_name].aggregated_spectrum.spectrum
        if not any(line.get_label() == mean_spec.label for line in ax_.get_lines()):
            ax_.plot(
                mean_spec.ramanshift,
                mean_spec.intensity,
                label=mean_spec.label,
                **RAW_MEAN_SPEC_FMT,
            )

    ax_.legend(fontsize=10)


def raw_data_spectra_plot(
    aggregated_spectra: Dict[RegionNames, AggregatedSampleSpectrumFitResult],
    export_paths: ExportPathSettings,
) -> ExportResult:
    regions = settings.default_regions
    sources = list(
        set(source for i in aggregated_spectra.values() for source in i.sources)
    )
    sample_id = "-".join(
        set(i.aggregated_spectrum.sample_id for i in aggregated_spectra.values())
    )
    valid_regions = filter_regions_for_spectrum(regions, sources[0].read.spectrum)

    destfile = export_paths.plots_dir.joinpath(f"{sample_id}_mean.png")
    destfile.parent.mkdir(exist_ok=True, parents=True)

    nrows, ncols = 2, 3
    plot_region_axes = get_plot_region_axes(nrows=nrows, regions=valid_regions)
    _, ax = plt.subplots(nrows, ncols, figsize=(18, 12))

    for spec_source in sources:
        for region_name, spec_region in spec_source.processed.processed_spectra:
            plot_spectrum(
                ax,
                spec_region,
                spec_source,
                region_name,
                aggregated_spectra,
                valid_regions,
                plot_region_axes,
            )

    plt.suptitle(f"Mean {sample_id}", fontsize=16)
    plt.savefig(
        destfile,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    _msg = f"raw_data_spectra_plot saved:\n{destfile}"
    logger.debug(_msg)
    return ExportResult(target=destfile, message=_msg)
