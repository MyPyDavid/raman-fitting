import pandas as pd

from raman_fitting.exporting.plotting import fit_spectrum_plot, raw_data_export

import logging

logger = logging.getLogger(__name__)


class ExporterError(Exception):
    """Error occured during the exporting functions"""


class Exporter:
    """
    The Exporter class handles all the exporting of spectra and models
    into figures and xlsx files.

    """

    def __init__(self, arg, raw_out=True, plot=True, model_names_prefix=["1st", "2nd"]):
        self.raw_out = raw_out
        self.plot = plot
        try:
            self.delegator(arg)
        except ExporterError:
            logger.warning(
                f"{self.__class__.__qualname__} failed export from {type(arg)}"
            )
        except Exception as e:
            logger.error(
                f"{self.__class__.__qualname__} failed export with unexpected error {e}"
            )

    # Exporting and Plotting
    def delegator(self, arg):
        self.fitter = arg
        if "Fitter" in type(arg).__name__:
            self.fitter = arg
            self.split_results()

            if self.raw_out:
                self.raw_export()

            if self.plot:
                self.export_fitting_plotting_models()
        elif isinstance(arg, list):
            # "list" in type([]).__name__:
            # FIXME
            try:
                self.export_from_list(arg)
            except Exception as e:
                logger.error(
                    "f{self.__class__.__qualname__} failed export from list", e
                )
        else:
            logger.warning(
                "f{self.__class__.__qualname__} failed export from unknown arg type {type(arg)}"
            )
            raise ExporterError

    def export_from_list(self, arg):
        fitter_args = [i for i in arg if hasattr(arg, "fitter")]
        if fitter_args:
            FitRes = pd.concat(
                [
                    val.FitParameters
                    for exp in fitter_args
                    for k, val in exp.fitter.FitResults.items()
                ]
            )
            _info = fitter_args[0].fitter.info
            # self.fitter[0].fitter.info
            self.export_fitparams_grp_per_model(FitRes, _info)

    def export_fitparams_grp_per_model(self, FitRes, _info):
        DestGrpDir = _info.get("DestGrpDir")
        grpnm = _info["SampleGroup"]
        for pknm, pkgrp in FitRes.groupby(level=0):
            peak_destpath = DestGrpDir.joinpath(f"{grpnm}_FitParameters_{pknm}")
            pkgrp.dropna(axis=1).to_excel(
                peak_destpath.with_suffix(".xlsx"), index=False
            )

    def raw_export(self):
        raw_data_export(self.fitter.spectra_arg.fitting_spectra)

    def split_results(self):
        pass
        # self._2nd = _2nd
        # _1st = {k:val for k,val in self.fitter.FitResults.items() if k.startswith('1st')}
        # self._1st = _1st

    def export_fitting_plotting_models(self):
        pars1, pars2 = [], []

        _1st = {
            k: val for k, val in self.fitter.FitResults.items() if k.startswith("1st")
        }
        _2nd = {
            k: val for k, val in self.fitter.FitResults.items() if k.startswith("2nd")
        }

        for modname_2, fitres_2 in _2nd.items():

            self.export_xls_from_spec(fitres_2)
            pars2.append(fitres_2.FitParameters)
            for modname_1, fitres_1 in _1st.items():
                self.export_xls_from_spec(fitres_1)
                try:
                    fit_spectrum_plot(
                        modname_1,
                        modname_2,
                        fitres_1,
                        fitres_2,
                        plot_Annotation=True,
                        plot_Residuals=True,
                    )
                except Exception as e:
                    print(
                        f"Error fit_spectrum_plot:{modname_1}, {fitres_1.raw_data_col}.\n {e}"
                    )
                pars1.append(fitres_1.FitParameters)
        return pd.concat(pars1, sort=False), pd.concat(pars2, sort=False)

    def export_xls_from_spec(self, res_peak_spec):
        try:
            # sID = res_peak_spec.extrainfo['SampleID']
            # peak_destpath = res_peak_spec.extrainfo['DestFittingComps.unique()[0].joinpath(f'Model_{res_peak_spec.peak_model}_{sID}')
            # peak_destpath_extra = res_peak_spec.extrainfo.DestFittingComps.unique()[0].joinpath(f'Extra_{res_peak_spec.peak_model}_{sID}')
            res_peak_spec.FitComponents.to_excel(
                res_peak_spec.extrainfo["DestFittingModel"].with_suffix(".xlsx"),
                index=False,
            )
            # res_peak_spec.extrainfo.to_excel(peak_destpath_extra.with_suffix('.xlsx'), index=False)
        except Exception as e:
            print("Error export_xls_from_spec", e)
        # IDEA define fuction for exporting all the indexes _all_index_export
        # index = RamanExport().export_FitParams_Grp(FitParams1, FitParams2, export_info_out, grpnm,sID)
        # all_index.append(index)
        # pars_index = pd.DataFrame(*all_index,columns=list(GrpNames.sGrp_cols[0:2] +('PeakModel','DestPars')))
        # pars_index.to_excel( export_info_out.get('DestGrpDir').joinpath(f'{sGr}_index.xlsx'))
