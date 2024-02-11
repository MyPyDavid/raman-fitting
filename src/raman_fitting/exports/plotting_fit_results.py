# ruff: noqa
from typing import Dict

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams.update({"font.size": 14})

from raman_fitting.models.splitter import WindowNames
from raman_fitting.delegating.models import AggregatedSampleSpectrumFitResult


#  TODO fix big spectrum plot


def fit_spectrum_plot(
    aggregated_spectra: Dict[WindowNames, AggregatedSampleSpectrumFitResult],
    plot_Annotation=True,
    plot_Residuals=True,
):  # pragma: no cover
    # %%
    res1_peak_spec.extrainfo["SampleID"]
    SampleBgmean_col = res1_peak_spec.raw_data_col

    FitData_1st = res1_peak_spec.FitComponents
    Model_data_col_1st = res1_peak_spec.model_name
    compscols_1st = [
        i for i in FitData_1st.columns if i.endswith("_") and not i.startswith("Si")
    ]

    FitData_2nd = res2_peak_spec.FitComponents
    Model_data_col_2nd = res2_peak_spec.model_name
    compscols_2nd = [i for i in FitData_2nd.columns if i.endswith("_")]

    FitPars, FitPars_2nd = res1_peak_spec.FitParameters, res2_peak_spec.FitParameters

    plt.figure(figsize=(28, 24))
    gs = gridspec.GridSpec(4, 1, height_ratios=[4, 1, 4, 1])
    ax = plt.subplot(gs[0])
    axRes = plt.subplot(gs[1])
    ax2nd = plt.subplot(gs[2])
    ax2ndRes = plt.subplot(gs[3])
    ax2ndRes.grid(True), axRes.grid(True, "both")
    ax2nd.grid(True), ax.grid(True, "both")
    ax.get_yaxis().set_tick_params(direction="in")
    ax.get_xaxis().set_tick_params(direction="in")
    ax.set_title(SampleBgmean_col)
    #                             '%s' %FileName)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.tick_params(which="both", direction="in")
    ax2nd.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax2nd.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax2nd.tick_params(which="both", direction="in")
    ax.set_facecolor("oldlace"), ax2nd.set_facecolor("oldlace")
    axRes.set_facecolor("oldlace"), ax2ndRes.set_facecolor("oldlace")
    ax2nd.plot(
        FitData_2nd["RamanShift"],
        FitData_2nd[Model_data_col_2nd],
        label=Model_data_col_2nd,
        lw=3,
        c="r",
    )
    ax2nd.plot(
        FitData_2nd["RamanShift"],
        FitData_2nd[res2_peak_spec.raw_data_col],
        label="Data",
        lw=3,
        c="grey",
        alpha=0.5,
    )
    if plot_Residuals:
        ax2ndRes.plot(
            FitData_2nd["RamanShift"],
            FitData_2nd[res2_peak_spec.raw_data_col] - FitData_2nd[Model_data_col_2nd],
            label="Residual",
            lw=3,
            c="k",
            alpha=0.8,
        )

    for fit_comp_col_2nd in compscols_2nd:  # automatic color cycle 'cyan' ...
        ax2nd.plot(
            FitData_2nd["RamanShift"],
            FitData_2nd[fit_comp_col_2nd],
            ls="--",
            lw=4,
            label=fit_comp_col_2nd,
        )
        center_col, height_col = (
            fit_comp_col_2nd + "center",
            fit_comp_col_2nd + "height",
        )
        ax2nd.annotate(
            f"{fit_comp_col_2nd}\n {FitPars_2nd[center_col].round(0).iloc[0]:.0f}",
            xy=(
                FitPars_2nd[center_col].iloc[0] * 0.97,
                0.8 * FitPars_2nd[height_col].iloc[0],
            ),
            xycoords="data",
        )
    ax2nd.set_ylim(-0.02, FitData_2nd[Model_data_col_2nd].max() * 1.5)
    ax.plot(
        FitData_1st["RamanShift"],
        FitData_1st[Model_data_col_1st],
        label=Model_data_col_1st,
        lw=3,
        c="r",
    )
    ax.plot(
        FitData_1st["RamanShift"],
        FitData_1st[res1_peak_spec.raw_data_col],
        label="Data",
        lw=3,
        c="grey",
        alpha=0.8,
    )

    if plot_Residuals:
        axRes.plot(
            FitData_1st["RamanShift"],
            FitData_1st[res1_peak_spec.raw_data_col] - FitData_1st[Model_data_col_1st],
            label="Residual",
            lw=3,
            c="k",
            alpha=0.8,
        )

    for fit_comp_col_1st in compscols_1st:  # automatic color cycle 'cyan' ...
        ax.plot(
            FitData_1st["RamanShift"],
            FitData_1st[fit_comp_col_1st],
            ls="--",
            lw=4,
            label=fit_comp_col_1st,
        )
        center_col, height_col = (
            fit_comp_col_1st + "center",
            fit_comp_col_1st + "height",
        )
        ax.annotate(
            f"{fit_comp_col_1st}:\n {FitPars[center_col].round(0).iloc[0]:.0f}",
            xy=(FitPars[center_col].iloc[0] * 0.97, 0.7 * FitPars[height_col].iloc[0]),
            xycoords="data",
        )

    if "peaks" in peak1 and peak1.endswith("+Si"):
        ax.plot(
            FitData_1st["RamanShift"],
            FitData_1st["Si1_"],
            "b--",
            lw=4,
            label="Si_substrate",
        )
        if FitPars["Si1_fwhm"].iloc[0] > 1:
            ax.annotate(
                "Si_substrate:\n %.0f" % FitPars["Si1_center"],
                xy=(FitPars["Si1_center"] * 0.97, 0.8 * FitPars["Si1_height"]),
                xycoords="data",
            )
    if plot_Annotation:
        frsplit = res1_peak_spec.FitReport.split()
        if len(frsplit) > 200:
            fr = res1_peak_spec.FitReport.replace("prefix='D3_'", "prefix='D3_' \n")
        else:
            fr = res1_peak_spec.FitReport
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
        Report1 = ax.text(
            1.01,
            1,
            fr,
            transform=ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=props,
        )
        Report2 = ax2nd.text(
            1.01,
            0.7,
            res2_peak_spec.FitReport,
            transform=ax2nd.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=props,
        )

    (
        ax.legend(loc=1),
        ax.set_xlabel("Raman shift (cm$^{-1}$)"),
        ax.set_ylabel("normalized I / a.u."),
    )
    (
        ax2nd.legend(loc=1),
        ax2nd.set_xlabel("Raman shift (cm$^{-1}$)"),
        ax2nd.set_ylabel("normalized I / a.u."),
    )

    plt.savefig(
        res1_peak_spec.extrainfo["DestFittingModel"].with_suffix(".png"),
        dpi=100,
        bbox_extra_artists=(Report1, Report2),
        bbox_inches="tight",
    )
    plt.close()
