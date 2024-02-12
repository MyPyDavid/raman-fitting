from dataclasses import dataclass
from typing import Dict, Any
from raman_fitting.config.settings import (
    RunModes,
    get_run_mode_paths,
    ExportPathSettings,
)


from raman_fitting.exports.plotting_fit_results import fit_spectrum_plot
from raman_fitting.exports.plotting_raw_data import raw_data_spectra_plot
from raman_fitting.exports.file_table import raw_data_spectra_export


import pandas as pd
from loguru import logger


class ExporterError(Exception):
    """Error occured during the exporting functions"""


@dataclass
class ExportManager:
    run_mode: RunModes
    results: Dict[str, Any] | None = None

    def __post_init__(self):
        self.paths = get_run_mode_paths(self.run_mode)

    def export_files(self):
        # breakpoint() self.results
        exports = []
        for group_name, group_results in self.results.items():
            for sample_id, sample_results in group_results.items():
                export_dir = self.paths.results_dir / group_name / sample_id
                export_paths = ExportPathSettings(results_dir=export_dir)
                try:
                    raw_data_spectra_plot(
                        sample_results["fit_results"], export_paths=export_paths
                    )
                except Exception as exc:
                    logger.error(f"Plotting error, raw_data_spectra_plot: {exc}")
                try:
                    fit_spectrum_plot(
                        sample_results["fit_results"], export_paths=export_paths
                    )
                except Exception as exc:
                    logger.error(f"plotting error fit_spectrum_plot: {exc}")
                    raise exc from exc
                exports.append(
                    {
                        "sample": sample_results["fit_results"],
                        "export_paths": export_paths,
                    }
                )
        return exports


def raw_data_export(fitting_specs):  # pragma: no cover
    current_sample = fitting_specs[0].windowname, fitting_specs[0].sIDmean_col
    try:
        raw_data_spectra_plot(fitting_specs)
    except Exception as e:
        print("no extra Raw Data plots for {1} \n {0}".format(e, current_sample))
    try:
        raw_data_spectra_export(fitting_specs)
    except Exception as e:
        print("no extra Raw Data plots for {1} \n {0}".format(e, current_sample))


class _Exporter:
    """
    The Exporter class handles all the exporting of spectra and models
    into figures and xlsx files.

    """

    def __init__(
        self, arg, raw_out=True, plot=True, model_names_prefix=["first", "second"]
    ):
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

    def export_fitting_plotting_models(self):
        pars1, pars2 = [], []

        _first = {
            k: val for k, val in self.fitter.FitResults.items() if k.startswith("first")
        }
        _second = {
            k: val
            for k, val in self.fitter.FitResults.items()
            if k.startswith("second")
        }

        for modname_2, fitres_2 in _second.items():
            self.export_xls_from_spec(fitres_2)
            pars2.append(fitres_2.FitParameters)
            for modname_1, fitres_1 in _first.items():
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
