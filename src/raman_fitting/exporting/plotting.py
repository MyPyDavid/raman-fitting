#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:49:50 2020

@author: DW
"""
import matplotlib
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter, MultipleLocator

matplotlib.rcParams.update({"font.size": 14})

#%%

# TODO FIX PLOTTING PER PEAK MODEL
def plotting_info(windowname):
    axes = {
        "full": (0, 0),
        "low": (0, 1),
        "1st_order": (0, 2),
        "mid": (1, 1),
        "2nd_order": (1, 2),
        "normalization": (1, 0),
    }
    return axes.get(windowname)


def raw_data_export(fitting_specs):
    current_sample = fitting_specs[0].windowname, fitting_specs[0].sIDmean_col
    try:
        raw_data_spectra_plot(fitting_specs)
    except Exception as e:
        print("no extra Raw Data plots for {1} \n {0}".format(e, current_sample))
    try:
        raw_data_spectra_export(fitting_specs)
    except Exception as e:
        print("no extra Raw Data plots for {1} \n {0}".format(e, current_sample))


def raw_data_spectra_plot(fitting_specs):
    #    fitting_specs
    try:
        fig, ax = plt.subplots(2, 3, figsize=(18, 12))
        ax_wn = []

        for spec in fitting_specs:
            try:
                ax_wn = ax[plotting_info(spec.windowname)]
                #                spec.windowname
                _legend = True if "full" == spec.windowname else False
                spec.mean_spec.plot(
                    x="ramanshift",
                    y=spec.sID_rawcols,
                    ax=ax_wn,
                    alpha=0.5,
                    legend=_legend,
                )
                spec.mean_spec.plot(
                    x="ramanshift",
                    y=spec.sIDmean_col,
                    ax=ax_wn,
                    c="k",
                    alpha=0.7,
                    lw=3,
                    legend=_legend,
                )

                ax_wn.set_title(spec.windowname)
                #                _legend = True if 'full' in spec.windowname else False
                if _legend:
                    ax_wn.legend(fontsize=10)

            except:
                pass

        plt.suptitle(spec.sIDmean_col, fontsize=16)
        plt.savefig(
            spec.mean_info.DestRaw.unique()[0].joinpath(f"{spec.sIDmean_col}.png"),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()
    except Exception as e:
        print("no extra Raw Data plots: {0}".format(e))


def raw_data_spectra_export(fitting_specs):
    #    fitting_specs
    try:
        for spec in fitting_specs:
            #            spec.windowname, spec.sIDmean_col
            wnxl_outpath_spectra = spec.mean_info.DestRaw.unique()[0].joinpath(
                f"spectra_{spec.sIDmean_col}_{spec.windowname}.xlsx"
            )
            spec.mean_spec.to_excel(wnxl_outpath_spectra)

        _0_spec = fitting_specs[0]
        wnxl_outpath_info = _0_spec.mean_info.DestRaw.unique()[0].joinpath(
            f"info_{_0_spec.sIDmean_col}.xlsx"
        )
        _0_spec.mean_info.to_excel(wnxl_outpath_info)

    #            ax_wn = ax[plotting_info(spec.windowname)]
    except Exception as e:
        print("no extra Raw Data plots: {0}".format(e))


def fit_spectrum_plot(
    peak1,
    peak2,
    res1_peak_spec,
    res2_peak_spec,
    plot_Annotation=True,
    plot_Residuals=True,
):

    #%%
    sID = res1_peak_spec.extrainfo["SampleID"]
    SampleBgmean_col = res1_peak_spec.raw_data_col

    #    sID, DestPlotDir, SampleBgmean_col, FitData, FitModPeaks, FitData_2nd,comps, comps_2nd,out, out_2nd,
    FitData_1st = res1_peak_spec.FitComponents
    Model_peak_col_1st = res1_peak_spec.model_name
    Model_data_col_1st = res1_peak_spec.model_name
    # f'Model_{Model_peak_col_1st}'
    compscols_1st = [
        i for i in FitData_1st.columns if i.endswith("_") and not i.startswith("Si")
    ]
    #    FitReport_1st = res1_peak_spec.FitReport

    FitData_2nd = res2_peak_spec.FitComponents
    Model_peak_col_2nd = res2_peak_spec.model_name
    Model_data_col_2nd = res2_peak_spec.model_name
    # f'Model_{Model_peak_col_2nd}'
    compscols_2nd = [i for i in FitData_2nd.columns if i.endswith("_")]

    FitPars, FitPars_2nd = res1_peak_spec.FitParameters, res2_peak_spec.FitParameters

    fig = plt.figure(figsize=(28, 24))
    gs = gridspec.GridSpec(4, 1, height_ratios=[4, 1, 4, 1])
    ax = plt.subplot(gs[0])
    axRes = plt.subplot(gs[1])
    #                axAnn = plt.subplot(gs[1])
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
    #                for FitN in [PosInts_Bg,PosInts_Bg_2nd]:
    #                    fig,ax = plt.subplots(1,1,figsize=(12,12))
    #                if FitN.RamanShift.max() > 2300:
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
    #    ax2nd.plot(FitData_2nd['RamanShift'], comps_2nd['D1D1_'], color='lime',ls='--',lw=4,label='2*D')
    #    ax2nd.plot(FitData_2nd['RamanShift'], comps_2nd['D4D4_'], color='purple',ls='--',lw=4,label='2*D4')
    #    ax2nd.plot(FitData_2nd['RamanShift'], comps_2nd['GD1_'], color='pink',ls='--',lw=4,label='G+D1')
    ax2nd.set_ylim(-0.02, FitData_2nd[Model_data_col_2nd].max() * 1.5)
    #                else:
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

    #    ax.plot(FitData_1st['RamanShift'], FitData_1st['D_'], color='lime',ls='--',lw=4,label='D')
    #                ax.plot(FitData['RamanShift'], comps['D2_'], color='grey',ls='--',lw=4,label='D2')
    #    ax.plot(FitData_1st['RamanShift'], FitData_1st['D3_'], 'b--',lw=4,label='D3')
    #    ax.plot(FitData_1st['RamanShift'], FitData_1st['D4_'], color='purple',ls='--',lw=4,label='D4')
    if "peaks" in peak1:
        #        ax.plot(FitData_1st['RamanShift'], FitData_1st['D2_'], color='magenta',ls='--',lw=4,label='D2')
        #        ax.annotate('D2:\n %.0f'%FitPars['D2_center'],xy=(FitPars['D2_center']*0.97,0.8*FitPars['I_D2']),xycoords='data')
        if peak1.endswith("+Si"):
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
    #        if '6peaks' in FitModPeaks:
    #            ax.plot(FitData_1st['RamanShift'], FitData_1st['D5_'],  color='darkorange',ls='--',lw=4,label='D5')
    #            ax.annotate('D5:\n %.0f'%FitPars['D5_center'],xy=(FitPars['D5_center']*0.97,0.8*FitPars['I_D5']),xycoords='data')
    ##                    for colN,col in FitN.iteritems():
    #                        if 'RamanShift' in colN or colN.split('_')[-1] == 'count' or colN.split('_')[-1] == 'std' :
    #                            continue
    #                        w,i = FitN['RamanShift'].values,col.values
    #                        if 'mean' in colN:
    #                            ax.plot(w[::],i[::],label=colN)
    #                        else:
    #                            ax.scatter(w[::],i[::],label=colN)
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

    ax.legend(loc=1), ax.set_xlabel("Raman shift (cm$^{-1}$)"), ax.set_ylabel(
        "normalized I / a.u."
    )
    ax2nd.legend(loc=1), ax2nd.set_xlabel("Raman shift (cm$^{-1}$)"), ax2nd.set_ylabel(
        "normalized I / a.u."
    )
    #                plt.show()

    #    plt.show()
    plt.savefig(
        res1_peak_spec.extrainfo["DestFittingModel"].with_suffix(".png"),
        dpi=100,
        box_extra_artists=(Report1, Report2),
        bbox_inches="tight",
    )
    plt.close()
    #%%
