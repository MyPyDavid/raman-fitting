# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402
from dataclasses import dataclass, field
from typing import Sequence, Dict, Any, List

from pydantic import FilePath

from raman_fitting.config.path_settings import (
    RunModes,
    initialize_run_mode_paths,
    RunModePaths,
)
from raman_fitting.config import settings
from raman_fitting.delegators.processors import process_selection
from raman_fitting.delegators.utils import log_results
from raman_fitting.imports.files.index.factory import initialize_index

from raman_fitting.imports.files.models import RamanFileInfo
from raman_fitting.imports.files.selectors import (
    select_samples_from_index,
)

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.selectors import select_models_from_provided_models
from raman_fitting.models.splitter import RegionNames
from raman_fitting.exports.exporter import ExportManager, call_export_manager
from raman_fitting.imports.files.index.models import RamanFileIndex

from raman_fitting.delegators.models import (
    AggregatedSampleSpectrumFitResult,
)
from raman_fitting.delegators.pre_processing import (
    prepare_aggregated_spectrum_from_files,
)
from raman_fitting.models.deconvolution.base_model import LMFitModelCollection

from loguru import logger


@dataclass
class SampleGroupResult:
    sample_id: str
    region_results: Dict[RegionNames, AggregatedSampleSpectrumFitResult]


@dataclass
class GroupResult:
    group_name: str
    sample_results: Dict[str, SampleGroupResult]


@dataclass
class MainDelegatorResult:
    results: Dict[str, GroupResult]


@dataclass
class MainDelegator:
    """
    Main delegator for processing files containing Raman spectra.

    Creates plots and files in the config RESULTS directory.
    """

    run_mode: RunModes | None = field(default=None)
    use_multiprocessing: bool = field(default=False, repr=False)
    lmfit_models: LMFitModelCollection = field(
        default_factory=lambda: settings.default_models,
        repr=False,
    )
    fit_model_region_names: Sequence[RegionNames] = field(
        default=(RegionNames.FIRST_ORDER, RegionNames.SECOND_ORDER)
    )
    fit_model_specific_names: Sequence[str] | None = None
    select_sample_ids: Sequence[str] = field(default_factory=list)
    select_sample_groups: Sequence[str] = field(default_factory=list)
    index: RamanFileIndex | FilePath | None = field(default=None, repr=False)
    suffixes: List[str] = field(default_factory=lambda: [".txt"])
    exclusions: List[str] = field(default_factory=lambda: ["."])
    results: Dict[str, Any] = field(default_factory=dict, init=False)
    export: bool = True
    export_manager: ExportManager | None = None

    def __post_init__(self):
        self.index = initialize_index(
            self.index,
            self.exclusions,
            self.suffixes,
            self.run_mode_paths,
        )
        if not self.index:
            logger.info("Index is empty.")
            return
        self.selection = select_samples_from_index(
            self.index.raman_files, self.select_sample_groups, self.select_sample_ids
        )
        self.selected_models = select_models_from_provided_models(
            region_names=self.fit_model_region_names,
            model_names=self.fit_model_specific_names,
            provided_models=self.lmfit_models,
        )
        self.results = main_run(
            self.index,
            self.select_sample_groups,
            self.select_sample_ids,
            self.selected_models,
            self.use_multiprocessing,
            self.fit_model_region_names,
        )
        if self.export:
            self.export_manager = call_export_manager(
                self.run_mode,
                self.results,
            )

    @property
    def run_mode_paths(self) -> RunModePaths | None:
        if not self.run_mode:
            return None
        return initialize_run_mode_paths(self.run_mode)

    def select_fitting_model(
        self, region_name: RegionNames, model_name: str
    ) -> BaseLMFitModel:
        """Select a fitting model by region and model name."""
        try:
            return self.lmfit_models[region_name][model_name]
        except KeyError as exc:
            raise KeyError(f"Model {region_name} {model_name} not found.") from exc


def main_run(
    index: RamanFileIndex,
    select_sample_groups: Sequence[str],
    select_sample_ids: Sequence[str],
    selected_models: LMFitModelCollection,
    use_multiprocessing: bool,
    fit_model_region_names: Sequence[RegionNames],
) -> dict[str, dict[str, dict[RegionNames, AggregatedSampleSpectrumFitResult]]]:
    """Main function to run the processing of Raman spectra."""
    try:
        selection = select_samples_from_index(
            index.raman_files, select_sample_groups, select_sample_ids
        )
        logger.debug(f"Selected {len(selection)} samples for main run.")
    except ValueError as exc:
        logger.error(f"Selection failed. {exc}")
        return {}

    if not fit_model_region_names:
        logger.info("No model region names were selected.")
    if not selected_models:
        logger.info("No fit models were selected.")
    else:
        logger.debug(f"Selected models {len(selected_models)}")

    results, errors = process_selection(selection, selected_models, use_multiprocessing)
    log_results(results, errors)
    return results


def get_results_over_selected_models(
    raman_files: List[RamanFileInfo],
    models: LMFitModelCollection,
    fit_model_results: Dict[str, Any],
) -> Dict[RegionNames, AggregatedSampleSpectrumFitResult]:
    """Get results over selected models."""
    results = {}
    for region_name, region_grp in models.items():
        try:
            region_name = RegionNames(region_name)
        except ValueError as exc:
            logger.error(f"Region name {region_name} not found. {exc}")
            continue

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


def make_examples(
    **kwargs,
) -> dict[str, dict[str, dict[RegionNames, AggregatedSampleSpectrumFitResult]]]:
    """Create example instances of MainDelegator for testing."""
    delegator = MainDelegator(
        run_mode=RunModes.PYTEST,
        fit_model_specific_names=["2peaks", "2nd_4peaks"],
        export=False,
        **kwargs,
    )
    assert isinstance(delegator.index, RamanFileIndex)
    assert isinstance(delegator.run_mode_paths, RunModePaths)
    results = main_run(
        delegator.index,
        delegator.select_sample_groups,
        delegator.select_sample_ids,
        delegator.selected_models,
        delegator.use_multiprocessing,
        delegator.fit_model_region_names,
    )
    return results


if __name__ == "__main__":
    example_run = make_examples()
