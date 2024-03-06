#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:49:50 2020

@author: DW
"""
from typing import Dict


import matplotlib
import matplotlib.pyplot as plt

from raman_fitting.models.splitter import WindowNames
from raman_fitting.config.path_settings import (
    CLEAN_SPEC_WINDOW_NAME_PREFIX,
    ExportPathSettings,
)
from raman_fitting.exports.plot_formatting import PLOT_WINDOW_AXES
from raman_fitting.delegating.models import AggregatedSampleSpectrumFitResult

from loguru import logger

matplotlib.rcParams.update({"font.size": 14})


def raw_data_spectra_plot(
    aggregated_spectra: Dict[WindowNames, AggregatedSampleSpectrumFitResult],
    export_paths: ExportPathSettings,
):  # pragma: no cover
    if not aggregated_spectra:
        return

    sources = list(aggregated_spectra.values())[0].aggregated_spectrum.sources
    sample = sources[0].file_info.sample

    destfile = export_paths.plots.joinpath(f"{sample.id}_mean.png")
    destfile.parent.mkdir(exist_ok=True, parents=True)

    mean_fmt = dict(c="k", alpha=0.7, lw=3)
    sources_fmt = dict(alpha=0.4, lw=2)

    try:
        fig, ax = plt.subplots(2, 3, figsize=(18, 12))

        for _window_name, window_agg in aggregated_spectra.items():
            mean_spec = window_agg.aggregated_spectrum.spectrum
            window_name = mean_spec.window_name
            ax_window = ax[PLOT_WINDOW_AXES[window_name]]
            selected_processed_data = f"{CLEAN_SPEC_WINDOW_NAME_PREFIX}{window_name}"
            # plot the mean aggregated spectrum
            ax_window.plot(
                mean_spec.ramanshift,
                mean_spec.intensity,
                label=mean_spec.label,
                **mean_fmt,
            )

            for spec_source in sources:
                _legend = True if "full" == window_name else False
                spec_windows = spec_source.processed.clean_spectrum.spec_windows
                spec = spec_windows[selected_processed_data]
                # plot each of the data sources
                ax_window.plot(
                    spec.ramanshift,
                    spec.intensity,
                    label=spec_source.file_info.file.stem,
                    **sources_fmt,
                )

                ax_window.set_title(window_name)
                if _legend:
                    ax_window.legend(fontsize=10)

        plt.suptitle(f"Mean {sample.id}", fontsize=16)
        plt.savefig(
            destfile,
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()
        logger.debug(f"raw_data_spectra_plot saved:\n{destfile}")
    except Exception as exc:
        logger.error(f"raw_data_spectra_plot failed:\n{exc}")
        raise exc from exc


def plot_despike_Z(x):
    fig, ax = plt.subplots(2)
    ax.plot(x=x, y=["Zt", "Z_t_filtered"], alpha=0.5)
    ax.plot(x=x, y=["input_intensity", "despiked_intensity"], alpha=0.8)
    plt.show()
    plt.close()
