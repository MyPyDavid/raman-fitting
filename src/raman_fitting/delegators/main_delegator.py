# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402
from pathlib import Path
from typing import Sequence, Dict, Any, List, Union

from raman_fitting.config.path_settings import (
    RunModes,
    initialize_run_mode_paths,
    RunModePaths,
)
from raman_fitting.config import settings
from raman_fitting.delegators.processors import process_selection
from raman_fitting.delegators.utils import log_results
from raman_fitting.imports.files.index.factory import initialize_index

from raman_fitting.imports.files.models import RamanFileInfo, RamanFileInfoSet
from raman_fitting.imports.files.selectors import (
    select_samples_from_index,
)

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
from raman_fitting.models.deconvolution.base_model import (
    LMFitModelCollection,
    BaseLMFitModel,
)

from loguru import logger

from typing import Optional
from datetime import datetime, timezone
import attr

UTC = timezone.utc


# Using attrs with modern patterns
@attr.define(slots=True, frozen=True)
class SampleGroupResult:
    sample_id: str
    region_results: dict[RegionNames, AggregatedSampleSpectrumFitResult]


@attr.define(slots=True)
class GroupResult:
    group_name: str
    sample_results: dict[str, SampleGroupResult]

    def __getattr__(self, name: str) -> SampleGroupResult:
        """Enable dot notation access for samples."""
        if name in self.sample_results:
            return self.sample_results[name]
        raise AttributeError(
            f"Sample '{name}' not found in group '{self.group_name}'. "
            f"Available samples: {', '.join(sorted(self.sample_results.keys()))}"
        )

    def get_sample_ids(self) -> set[str]:
        """Get all sample IDs in this group."""
        return set(self.sample_results.keys())


@attr.define(slots=True)
class MainDelegatorResult:
    results: dict[str, GroupResult]
    created_at: datetime = attr.field(
        factory=lambda: datetime.now(UTC),
        metadata={"description": "UTC timestamp when results were created"},
    )

    def __getattr__(self, name: str) -> GroupResult:
        """Enable dot notation access for groups."""
        if name in self.results:
            return self.results[name]
        raise AttributeError(
            f"Group '{name}' not found. Available groups: {', '.join(sorted(self.results.keys()))}"
        )

    def filter_by_groups(self, group_names: Sequence[str]) -> "MainDelegatorResult":
        filtered_results = {
            name: result for name, result in self.results.items() if name in group_names
        }
        return MainDelegatorResult(
            results=filtered_results,
            created_at=self.created_at,
            created_by=self.created_by,
        )

    def filter_by_samples(self, sample_ids: Sequence[str]) -> "MainDelegatorResult":
        filtered_results = {}
        for group_name, group_result in self.results.items():
            filtered_samples = {
                sample_id: result
                for sample_id, result in group_result.sample_results.items()
                if sample_id in sample_ids
            }
            if filtered_samples:
                filtered_results[group_name] = GroupResult(
                    group_name=group_name, sample_results=filtered_samples
                )
        return MainDelegatorResult(
            results=filtered_results,
            created_at=self.created_at,
            created_by=self.created_by,
        )


@attr.define
class MainDelegator:
    run_mode: Optional[RunModes] = attr.field(default=None)
    use_multiprocessing: bool = attr.field(default=False, repr=False)
    lmfit_models: LMFitModelCollection = attr.field(
        factory=lambda: settings.default_models, repr=False
    )
    fit_model_region_names: Sequence[RegionNames] = attr.field(
        default=(RegionNames.FIRST_ORDER, RegionNames.SECOND_ORDER)
    )
    fit_model_specific_names: Optional[Sequence[str]] = attr.field(default=None)
    selected_models: dict[str, dict[str, BaseLMFitModel]] = attr.field(factory=dict)
    select_sample_ids: Sequence[str] = attr.field(factory=list)
    select_sample_groups: Sequence[str] = attr.field(factory=list)
    selection: Sequence[RamanFileInfo] | RamanFileInfoSet = attr.field(factory=list)
    index: Optional[Union[RamanFileIndex, Path]] = attr.field(default=None, repr=False)
    suffixes: list[str] = attr.field(factory=lambda: [".txt"])
    exclusions: list[str] = attr.field(factory=lambda: ["."])
    results: Union[dict[str, Any], MainDelegatorResult] = attr.field(factory=dict)
    export: bool = attr.field(default=True)
    export_manager: Optional[ExportManager] = attr.field(default=None)

    def __attrs_post_init__(self):
        """Initialize after instance creation."""
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

        self.results = self.run()

    @property
    def run_mode_paths(self) -> Optional[RunModePaths]:
        if not self.run_mode:
            return None
        return initialize_run_mode_paths(self.run_mode)

    def run(self) -> MainDelegatorResult:
        """Execute the main processing pipeline and return results."""
        if not self.index:
            raise ValueError("Index must be initialized before running processing")

        if not self.selection:
            raise ValueError("No samples were selected for processing")

        if not self.selected_models:
            raise ValueError("No models were selected for processing")

        logger.info(
            f"Processing {len(self.selection)} samples with {len(self.selected_models)} models"
        )

        results = main_run(
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
                results,
            )

        return MainDelegatorResult(results=results, created_at=datetime.now(UTC))


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
            region=region_name,
            aggregated_spectrum=aggregated_spectrum,
            fit_model_results=fit_model_results,
        )
        results[region_name] = fit_region_results
    return results
