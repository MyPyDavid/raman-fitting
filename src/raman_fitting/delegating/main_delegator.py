# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Any

from raman_fitting.config.path_settings import (
    RunModes,
    ERROR_MSG_TEMPLATE,
    initialize_run_mode_paths,
)
from raman_fitting.config import settings

from raman_fitting.imports.models import RamanFileInfo

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.splitter import RegionNames
from raman_fitting.exports.exporter import ExportManager
from raman_fitting.imports.files.file_indexer import (
    RamanFileIndex,
    groupby_sample_group,
    groupby_sample_id,
    IndexSelector,
    initialize_index_from_source_files,
)

from raman_fitting.delegating.models import (
    AggregatedSampleSpectrumFitResult,
)
from raman_fitting.delegating.pre_processing import (
    prepare_aggregated_spectrum_from_files,
)
from raman_fitting.types import LMFitModelCollection
from raman_fitting.delegating.run_fit_spectrum import run_fit_over_selected_models


from loguru import logger


@dataclass
class MainDelegator:
    # IDEA Add flexible input handling for the cli, such a path to dir, or list of files
    #  or create index when no kwargs are given.
    """
    Main delegator for the processing of files containing Raman spectra.

    Creates plots and files in the config RESULTS directory.
    """

    run_mode: RunModes
    use_multiprocessing: bool = False
    lmfit_models: LMFitModelCollection = field(
        default_factory=lambda: settings.default_models
    )
    fit_model_region_names: Sequence[RegionNames] = field(
        default=(RegionNames.first_order, RegionNames.second_order)
    )
    fit_model_specific_names: Sequence[str] | None = None
    sample_ids: Sequence[str] = field(default_factory=list)
    sample_groups: Sequence[str] = field(default_factory=list)
    index: RamanFileIndex = None
    selection: Sequence[RamanFileInfo] = field(init=False)
    selected_models: Sequence[RamanFileInfo] = field(init=False)

    results: Dict[str, Any] | None = field(default=None, init=False)
    export: bool = True

    def __post_init__(self):
        run_mode_paths = initialize_run_mode_paths(self.run_mode)
        if self.index is None:
            raman_files = run_mode_paths.dataset_dir.glob("*.txt")
            index_file = run_mode_paths.index_file
            self.index = initialize_index_from_source_files(
                files=raman_files, index_file=index_file, force_reindex=True
            )

        self.selection = self.select_samples_from_index()
        self.selected_models = self.select_models_from_provided_models()
        self.main_run()
        if self.export:
            self.exports = self.call_export_manager()

    def select_samples_from_index(self) -> Sequence[RamanFileInfo]:
        index = self.index
        # breakpoint()
        index_selector = IndexSelector(
            **dict(
                raman_files=index.raman_files,
                sample_groups=self.sample_groups,
                sample_ids=self.sample_ids,
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

    # region_names:List[RegionNames], model_names: List[str]
    def select_models_from_provided_models(self) -> LMFitModelCollection:
        selected_region_names = self.fit_model_region_names
        selected_model_names = self.fit_model_specific_names
        selected_models = {}
        for region_name, all_region_models in self.lmfit_models.items():
            if region_name not in selected_region_names:
                continue
            if not selected_model_names:
                selected_models[region_name] = all_region_models
                continue
            selected_region_models = {}
            for mod_name, mod_val in all_region_models.items():
                if mod_name not in selected_model_names:
                    continue
                selected_region_models[mod_name] = mod_val

            selected_models[region_name] = selected_region_models
        return selected_models

    def select_fitting_model(
        self, region_name: RegionNames, model_name: str
    ) -> BaseLMFitModel:
        try:
            return self.lmfit_models[region_name][model_name]
        except KeyError as exc:
            raise KeyError(f"Model {region_name} {model_name} not found.") from exc

    def main_run(self):
        selection = self.select_samples_from_index()
        if not self.fit_model_region_names:
            logger.info("No model region names were selected.")
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
                if len(unique_positions) <= len(sgrp):
                    #  handle edge-case, multiple source files for a single position on a sample
                    _error_msg = f"Handle multiple source files for a single position on a sample, {group_name} {sample_id}"
                    results[group_name][sample_id]["errors"] = _error_msg
                    logger.debug(_error_msg)
                model_result = run_fit_over_selected_models(
                    sgrp,
                    self.selected_models,
                    use_multiprocessing=self.use_multiprocessing,
                )
                results[group_name][sample_id]["fit_results"] = model_result
        self.results = results


def get_results_over_selected_models(
    raman_files: List[RamanFileInfo], models: LMFitModelCollection, fit_model_results
) -> Dict[RegionNames, AggregatedSampleSpectrumFitResult]:
    results = {}
    for region_name, region_grp in models.items():
        aggregated_spectrum = prepare_aggregated_spectrum_from_files(
            region_name, raman_files
        )
        if aggregated_spectrum is None:
            continue
        fit_region_results = AggregatedSampleSpectrumFitResult(
            region_name=region_name,
            aggregated_spectrum=aggregated_spectrum,
            fit_model_results=fit_model_results,
        )
        results[region_name] = fit_region_results
    return results


def make_examples():
    # breakpoint()
    _main_run = MainDelegator(
        run_mode="pytest", fit_model_specific_names=["2peaks", "3peaks", "2nd_4peaks"]
    )
    _main_run.main_run()
    return _main_run


if __name__ == "__main__":
    example_run = make_examples()
