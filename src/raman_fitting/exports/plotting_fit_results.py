# ruff: noqa
from typing import Dict

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter, MultipleLocator

matplotlib.rcParams.update({"font.size": 14})

from raman_fitting.config.settings import ExportPathSettings
from raman_fitting.models.splitter import WindowNames
from raman_fitting.delegating.models import AggregatedSampleSpectrumFitResult

from loguru import logger
#  TODO fix big spectrum plot


def fit_spectrum_plot(
    aggregated_spectra: Dict[WindowNames, AggregatedSampleSpectrumFitResult],
    export_paths: ExportPathSettings | None = None,
    plot_Annotation=True,
    plot_Residuals=True,
):  # pragma: no cover
    # %%
    first_order = aggregated_spectra[WindowNames.first_order]
    second_order = aggregated_spectra[WindowNames.second_order]

    sources = first_order.aggregated_spectrum.sources
    sample = sources[0].file_info.sample

    first_model = first_order.fit_model_results["4peaks"]
    first_result = first_model.fit_result
    first_components = first_model.fit_result.components
    first_eval_comps = first_model.fit_result.eval_components()
    first_model_name = first_model.model.name
    first_pars = first_model.fit_result.best_values

    if second_order.fit_model_results:
        second_model = second_order.fit_model_results["2nd_4peaks"]
        second_result = second_model.fit_result
        second_components = second_model.fit_result.components
        second_eval_comps = second_model.fit_result.eval_components()
        second_model_name = second_model.model.name
        second_pars = second_model.fit_result.best_values
    else:
        second_order = None
        second_components = []
        second_result = None

    plt.figure(figsize=(28, 24))
    gs = gridspec.GridSpec(4, 1, height_ratios=[4, 1, 4, 1])
    ax = plt.subplot(gs[0])
    ax.grid(True, "both")
    axRes = plt.subplot(gs[1])
    axRes.grid(True, "both")
    if second_order:
        ax2nd = plt.subplot(gs[2])
        ax2nd.grid(True)
        ax2ndRes = plt.subplot(gs[3])
        ax2ndRes.grid(True)
    ax.get_yaxis().set_tick_params(direction="in")
    ax.get_xaxis().set_tick_params(direction="in")
    ax.set_title(f"{sample.id}")

    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.tick_params(which="both", direction="in")
    ax.set_facecolor("oldlace")
    axRes.set_facecolor("oldlace")
    if second_order:
        ax2nd.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax2nd.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax2nd.tick_params(which="both", direction="in")
        ax2nd.set_facecolor("oldlace")
        ax2ndRes.set_facecolor("oldlace")
        ax2nd.plot(
            second_model.spectrum.ramanshift,
            second_result.best_fit,
            label=second_model_name,
            lw=3,
            c="r",
        )
        ax2nd.plot(
            second_model.spectrum.ramanshift,
            second_result.data,
            label="Data",
            lw=3,
            c="grey",
            alpha=0.5,
        )
        if plot_Residuals:
            ax2ndRes.plot(
                second_model.spectrum.ramanshift,
                second_result.residual,
                label="Residual",
                lw=3,
                c="k",
                alpha=0.8,
            )

    for _component in second_components:  # automatic color cycle 'cyan' ...
        peak_name = _component.prefix.rstrip("_")
        ax2nd.plot(
            second_model.spectrum.ramanshift,
            second_eval_comps[_component.prefix],
            ls="--",
            lw=4,
            label=peak_name,
        )
        center_col = _component.prefix + "center"
        ax2nd.annotate(
            f"{peak_name}\n {second_result.best_values[center_col]:.0f}",
            xy=(
                second_result.best_values[center_col] * 0.97,
                0.8 * second_result.params[_component.prefix + "height"].value,
            ),
            xycoords="data",
        )
        ax2nd.set_ylim(-0.02, second_result.data.max() * 1.5)
    ax.plot(
        first_model.spectrum.ramanshift,
        first_result.best_fit,
        label=first_model_name,
        lw=3,
        c="r",
    )
    ax.plot(
        first_model.spectrum.ramanshift,
        first_result.data,
        label="Data",
        lw=3,
        c="grey",
        alpha=0.8,
    )

    if plot_Residuals:
        axRes.plot(
            first_model.spectrum.ramanshift,
            first_result.residual,
            label="Residual",
            lw=3,
            c="k",
            alpha=0.8,
        )

    for _component in first_components:  # automatic color cycle 'cyan' ...
        peak_name = _component.prefix.rstrip("_")
        ax.plot(
            first_model.spectrum.ramanshift,
            first_eval_comps[_component.prefix],
            ls="--",
            lw=4,
            label=peak_name,
        )
        center_col = _component.prefix + "center"
        ax.annotate(
            f"{peak_name}:\n {first_result.best_values[center_col]:.0f}",
            xy=(
                first_result.best_values[center_col] * 0.97,
                0.7 * first_result.params[_component.prefix + "height"].value,
            ),
            xycoords="data",
        )

    for si_comp in [i for i in first_components if i.prefix.startswith("Si")]:
        si_result = si_comp
        #  TODO should be si_fit_results
        ax.plot(
            first_model.spectrum.ramanshift,
            first_eval_comps[si_comp.prefix],
            "b--",
            lw=4,
            label="Si_substrate",
        )
        if si_result.params[si_comp.prefix + "fwhm"] > 1:
            ax.annotate(
                "Si_substrate:\n %.0f" % si_result.params["Si1_center"].value,
                xy=(
                    si_result.params["Si1_center"].value * 0.97,
                    0.8 * si_result.params["Si1_height"].value,
                ),
                xycoords="data",
            )
    if plot_Annotation:
        fit_report = first_result.fit_report()
        if len(fit_report) > -1:  #  TODO remove
            fit_report = fit_report.replace("prefix='D3_'", "prefix='D3_' \n")
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

        Report1 = ax.text(
            1.01,
            1,
            fit_report,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=props,
        )
        _bbox_artists = (Report1,)
        if second_result:
            Report2 = ax2nd.text(
                1.01,
                0.7,
                second_result.fit_report(),
                transform=ax2nd.transAxes,
                fontsize=11,
                verticalalignment="top",
                bbox=props,
            )
            _bbox_artists = (Report1, Report2)

    (
        ax.legend(loc=1),
        ax.set_xlabel("Raman shift (cm$^{-1}$)"),
        ax.set_ylabel("normalized I / a.u."),
    )
    if second_order:
        (
            ax2nd.legend(loc=1),
            ax2nd.set_xlabel("Raman shift (cm$^{-1}$)"),
            ax2nd.set_ylabel("normalized I / a.u."),
        )
    if export_paths is not None:
        savepath = export_paths.plots.joinpath(f"Model_{first_model_name}").with_suffix(
            ".png"
        )
        plt.savefig(
            savepath,
            dpi=100,
            bbox_extra_artists=_bbox_artists,
            bbox_inches="tight",
        )
        logger.debug(f"Plot saved to {savepath}")
    plt.close()
