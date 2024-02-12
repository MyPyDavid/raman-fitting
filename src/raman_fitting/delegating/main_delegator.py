# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Any
from typing import TypeAlias


from raman_fitting.config.settings import (
    RunModes,
    ERROR_MSG_TEMPLATE,
)

from raman_fitting.imports.models import RamanFileInfo

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.deconvolution.base_model import (
    get_models_and_peaks_from_definitions,
)
from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.models.fit_models import SpectrumFitModel
from raman_fitting.models.splitter import WindowNames
from raman_fitting.exports.exporter import ExportManager
from raman_fitting.imports.files.file_indexer import (
    RamanFileIndex,
    initialize_index,
    groupby_sample_group,
    groupby_sample_id,
    IndexSelector,
)

from raman_fitting.delegating.models import (
    AggregatedSampleSpectrumFitResult,
)
from raman_fitting.delegating.pre_processing import (
    prepare_aggregated_spectrum_from_files,
)

from loguru import logger


LMFitModelCollection: TypeAlias = Dict[str, Dict[str, BaseLMFitModel]]
SpectrumFitModelCollection: TypeAlias = Dict[str, Dict[str, SpectrumFitModel]]


@dataclass
class MainDelegator:
    # IDEA Add flexible input handling for the cli, such a path to dir, or list of files
    #  or create index when no kwargs are given.
    """
    Main delegator for the processing of files containing Raman spectra.

    Input parameters is DataFrame of index
    Creates plots and files in the config RESULTS directory.
    """

    run_mode: RunModes
    lmfit_models: LMFitModelCollection = field(
        default_factory=get_models_and_peaks_from_definitions
    )
    fit_model_window_names: Sequence[WindowNames] = field(
        default=(WindowNames.first_order, WindowNames.second_order)
    )
    fit_model_specific_names: Sequence[str] | None = None
    sample_IDs: Sequence[str] = field(default_factory=list)
    sample_groups: Sequence[str] = field(default_factory=list)
    index: RamanFileIndex = field(default_factory=initialize_index)

    selection: Sequence[RamanFileInfo] = field(init=False)
    selected_models: Sequence[RamanFileInfo] = field(init=False)

    results: Dict[str, Any] | None = field(default=None, init=False)
    export: bool = True

    def __post_init__(self):
        self.selection = self.select_samples_from_index()
        self.selected_models = self.select_models_from_provided_models()
        self.main_run()
        if self.export:
            # breakpoint()
            self.exports = self.call_export_manager()

    def select_samples_from_index(self) -> Sequence[RamanFileInfo]:
        index = self.index
        # breakpoint()
        index_selector = IndexSelector(
            **dict(
                raman_files=index.raman_files,
                sample_groups=self.sample_groups,
                sample_IDs=self.sample_IDs,
            )
        )
        selection = index_selector.selection
        if not selection:
            logger.info("Selection was empty.")
        return selection

    def call_export_manager(self):
        # breakpoint()
        export = ExportManager(self.run_mode, self.results)
        exports = export.export_files()
        return exports

    # window_names:List[WindowNames], model_names: List[str]
    def select_models_from_provided_models(self) -> LMFitModelCollection:
        selected_window_names = self.fit_model_window_names
        selected_model_names = self.fit_model_specific_names
        selected_models = {}
        for window_name, all_window_models in self.lmfit_models.items():
            if window_name not in selected_window_names:
                continue
            if not selected_model_names:
                selected_models[window_name] = all_window_models
                continue
            selected_window_models = {}
            for mod_name, mod_val in all_window_models.items():
                if mod_name not in selected_model_names:
                    continue
                selected_window_models[mod_name] = mod_val

            selected_models[window_name] = selected_window_models
        return selected_models

    def select_fitting_model(
        self, window_name: WindowNames, model_name: str
    ) -> BaseLMFitModel:
        try:
            return self.lmfit_models[window_name][model_name]
        except KeyError as exc:
            raise ValueError(f"Model {window_name} {model_name} not found.") from exc

    def main_run(self):
        selection = self.select_samples_from_index()
        if not self.fit_model_window_names:
            logger.info("No model window names were selected.")
        if not self.selected_models:
            logger.info("No fit models were selected.")

        results = {}
        for group_name, grp in groupby_sample_group(selection):
            results[group_name] = {}
            for sample_id, sample_grp in groupby_sample_id(grp):
                sgrp = list(sample_grp)
                results[group_name][sample_id] = {}
                _error_msg = None

                if not sgrp:
                    _err = "group is empty"
                    _error_msg = ERROR_MSG_TEMPLATE.format(group_name, sample_id, _err)
                    logger.debug(_error_msg)
                    results[group_name][sample_id]["errors"] = _error_msg
                    continue

                unique_positions = {i.sample.position for i in sgrp}
                if not len(unique_positions) > len(sgrp):
                    # TODO handle edge-case, multiple source files for a single position on a sample
                    _error_msg = f"Handle multiple source files for a single position on a sample, {group_name} {sample_id}"
                    results[group_name][sample_id]["errors"] = _error_msg
                    logger.debug(_error_msg)
                # results[group_name][sample_id]['data_source'] = sgrp
                model_result = run_fit_over_selected_models(sgrp, self.selected_models)
                results[group_name][sample_id]["fit_results"] = model_result
        self.results = results
        # TODO add a FitResultModel for collection all the results
        # sample_result = {'group': grp, 'spec_fit': spec_fit, 'mean_spec': mean_spec}
        # results[group_name][sample_id].update(sample_result)


def run_fit_over_selected_models(
    raman_files: List[RamanFileInfo], models: LMFitModelCollection
) -> Dict[WindowNames, AggregatedSampleSpectrumFitResult]:
    results = {}
    for window_name, window_grp in models.items():
        aggregated_spectrum = prepare_aggregated_spectrum_from_files(
            window_name, raman_files
        )
        if aggregated_spectrum is None:
            continue
        fit_model_results = {}
        for model_name, model in window_grp.items():
            spectrum_fit = run_sample_fit_with_model(
                aggregated_spectrum.spectrum, model
            )
            fit_model_results[model_name] = spectrum_fit
        fit_window_results = AggregatedSampleSpectrumFitResult(
            window_name=window_name,
            aggregated_spectrum=aggregated_spectrum,
            fit_model_results=fit_model_results,
        )
        results[window_name] = fit_window_results
    return results


def run_sample_fit_with_model(
    spectrum: SpectrumData, model: BaseLMFitModel
) -> SpectrumFitModel:
    name = model.name
    window = model.window_name.name
    spec_fit = SpectrumFitModel(spectrum=spectrum, model=model)
    #  TODO include optional https://lmfit.github.io/lmfit-py/model.html#saving-and-loading-modelresults
    spec_fit.run_fit()
    logger.debug(
        f"Fit with model {name} on {window} success: {spec_fit.fit_result.success} in {spec_fit.elapsed_time:.2f}s."
    )
    # spec_fit.fit_result.plot(show_init=True)
    return spec_fit


def make_examples():
    # breakpoint()
    _main_run = MainDelegator(
        run_mode="pytest", fit_model_specific_names=["2peaks", "4peaks"]
    )
    _main_run.main_run()
    return _main_run


if __name__ == "__main__":
    RamanIndex = make_examples()
