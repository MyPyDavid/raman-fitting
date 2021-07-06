""" Multiprocessing implementation """
# flake8: noqa

from functools import partial
from multiprocessing import Pool
from os import cpu_count


class MultiRun:
    """
    This class enable the main fitting loop to be run in multiple processors
    """

    # TODO Add multi processing functions

    def __init__(self, spectra):
        self._spectra = spectra


def _previous():
    def worker_wrapper(arg):
        args, kwargs = arg
        return worker(*args, **kwargs)

    def compute_desc_pool(coord, radius, coords, feat, verbose):
        compute_desc(coord, radius, coords, feat, verbose)

    # results = run_fitting_multi(x,y,export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col, model_options = model_option)

    def run_fitting_multi(
        x,
        y,
        export_info=info_spec_1st,
        PreFit=False,
        raw_data_col=spec_1st.sIDmean_col,
        model_options=model_option,
    ):
        return

    def fit_peak(peak_model, *args, **kwargs):
        Fit_1stOrder_Carbon(args, peak_model=peak_model, **kwargs)

    def multi_fit(
        x,
        y,
        peak_model=peak_model,
        export_info=info_spec_1st,
        PreFit=False,
        raw_data_col=spec_1st.sIDmean_col,
    ):
        Fit_1stOrder_Carbon(
            x,
            y,
            peak_model=peak_model,
            export_info=info_spec_1st,
            PreFit=False,
            raw_data_col=spec_1st.sIDmean_col,
        )

    # start_fitting(fitting_specs)
    def run_multi_fitting(peak_model, *args, **kwargs):
        # TODO fix multiprocessing fitting run
        for peak_model in model_options:
            FittingComps, FittingParams, FitReport = Fit_1stOrder_Carbon(
                x,
                y,
                peak_model=peak_model,
                export_info=info_spec_1st,
                PreFit=False,
                raw_data_col=spec_1st.sIDmean_col,
            )
            Result_peak = Result_peak_nt(
                FittingComps,
                FittingParams,
                info_spec_1st,
                peak_model,
                spec_1st.sIDmean_col,
                FitReport,
            )
            results.update({peak_model: Result_peak})

    def _main():
        with Pool(cpu_count() - 2) as pool:
            try:
                results = run_multi_fitting(
                    peak_model,
                )
                pool.map(run_multi_fitting(peak_model), par_files_run)
            except Exception as e:
                print("run_multi_fitting error:", e)
                logger.error("run_multi_fitting error: {0}".format(e))
