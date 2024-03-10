#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:49:50 2020

@author: DW
"""

from typing import Dict


import matplotlib
import matplotlib.pyplot as plt

from raman_fitting.models.splitter import RegionNames
from raman_fitting.config.path_settings import (
    CLEAN_SPEC_REGION_NAME_PREFIX,
    ExportPathSettings,
)
from raman_fitting.exports.plot_formatting import PLOT_REGION_AXES
from raman_fitting.delegating.models import AggregatedSampleSpectrumFitResult

from loguru import logger

matplotlib.rcParams.update({"font.size": 14})


def raw_data_spectra_plot(
    aggregated_spectra: Dict[RegionNames, AggregatedSampleSpectrumFitResult],
    export_paths: ExportPathSettings,
):  # pragma: no cover
    if not aggregated_spectra:
        return
    # breakpoint()
    sources = list(aggregated_spectra.values())[0].aggregated_spectrum.sources
    sample_id = "-".join(set(i.file_info.sample.id for i in sources))

    destfile = export_paths.plots.joinpath(f"{sample_id}_mean.png")
    destfile.parent.mkdir(exist_ok=True, parents=True)

    mean_fmt = dict(c="k", alpha=0.7, lw=3)
    sources_fmt = dict(alpha=0.4, lw=2)

    _, ax = plt.subplots(2, 3, figsize=(18, 12))

    for spec_source in sources:
        for (
            source_region_label,
            source_region,
        ) in spec_source.processed.clean_spectrum.spec_regions.items():
            _source_region_name = source_region.region_name.split(
                CLEAN_SPEC_REGION_NAME_PREFIX
            )[-1]
            if _source_region_name not in PLOT_REGION_AXES:
                continue
            ax_ = ax[PLOT_REGION_AXES[_source_region_name]]
            ax_.plot(
                source_region.ramanshift,
                source_region.intensity,
                label=f"{spec_source.file_info.file.stem}",
                **sources_fmt,
            )
            ax_.set_title(_source_region_name)
            if _source_region_name in aggregated_spectra:
                mean_spec = aggregated_spectra[
                    _source_region_name
                ].aggregated_spectrum.spectrum
                # plot the mean aggregated spectrum
                ax_.plot(
                    mean_spec.ramanshift,
                    mean_spec.intensity,
                    label=mean_spec.label,
                    **mean_fmt,
                )

            if _source_region_name == RegionNames.full:
                ax_.legend(fontsize=10)

    plt.suptitle(f"Mean {sample_id}", fontsize=16)
    plt.savefig(
        destfile,
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()
    logger.debug(f"raw_data_spectra_plot saved:\n{destfile}")
