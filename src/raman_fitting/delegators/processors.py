from typing import Sequence

from loguru import logger

from raman_fitting.config.path_settings import ERROR_MSG_TEMPLATE
from raman_fitting.delegators.models import AggregatedSampleSpectrumFitResult
from raman_fitting.delegators.run_fit_spectrum import run_fit_over_selected_models
from raman_fitting.imports.files.models import RamanFileInfo
from raman_fitting.imports.files.selectors import (
    group_by_sample_group,
    group_by_sample_id,
)
from raman_fitting.models.deconvolution.base_model import LMFitModelCollection
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames


def process_selection(
    selection: Sequence[RamanFileInfo],
    selected_models: LMFitModelCollection,
    use_multiprocessing: bool,
) -> tuple[
    dict[str, dict[str, dict[RegionNames, AggregatedSampleSpectrumFitResult]]],
    list[str],
]:
    """Process the selection of samples."""
    selection_results, errors = {}, []
    for group_name, grp in group_by_sample_group(selection):
        group_result, _errors = process_group(
            group_name, grp, selected_models, use_multiprocessing
        )
        selection_results[group_name] = group_result
        if _errors:
            errors.append({group_name: _errors})
    return selection_results, errors


def process_group(
    group_name: str,
    grp: Sequence[RamanFileInfo],
    selected_models: LMFitModelCollection,
    use_multiprocessing: bool,
) -> tuple[dict[str, dict[RegionNames, AggregatedSampleSpectrumFitResult]], list[str]]:
    """Process a group of samples."""
    group_results = {}
    errors = []
    for sample_id, sample_id_grp in group_by_sample_id(grp):
        sample_result, _errors = process_sample(
            group_name,
            sample_id,
            sample_id_grp,
            selected_models,
            use_multiprocessing,
        )
        group_results[sample_id] = sample_result
        if _errors:
            errors.append({sample_id: _errors})
    return group_results, errors


def process_sample(
    group_name: str,
    sample_id: str,
    sample_id_grp: Sequence[RamanFileInfo],
    selected_models: LMFitModelCollection,
    use_multiprocessing: bool,
) -> tuple[dict[RegionNames, AggregatedSampleSpectrumFitResult], list[str]]:
    """Process a single sample."""
    errors = []
    if not sample_id_grp:
        _error_msg = ERROR_MSG_TEMPLATE.format(group_name, sample_id, "group is empty")
        logger.debug(_error_msg)
        errors.append(_error_msg)

    sample_id_grp = sorted(sample_id_grp, key=lambda x: x.sample.position)
    unique_positions = {i.sample.position for i in sample_id_grp}

    if len(unique_positions) < len(sample_id_grp):
        _error_msg = f"Handle multiple source files for a single position on a sample, {group_name} {sample_id}"
        logger.debug(_error_msg)
        errors.append(_error_msg)

    model_result = run_fit_over_selected_models(
        sample_id_grp,
        selected_models,
        use_multiprocessing=use_multiprocessing,
    )
    return model_result, errors
