from itertools import groupby
from typing import Sequence

from raman_fitting.imports.files.models import RamanFileInfo, RamanFileInfoSet

from loguru import logger


def select_samples_from_index(
    raman_files: RamanFileInfoSet,
    select_sample_groups: Sequence[str],
    select_sample_ids: Sequence[str],
) -> Sequence[RamanFileInfo] | RamanFileInfoSet:
    if not raman_files:
        raise ValueError("Index file is empty.")

    if not any([select_sample_groups, select_sample_ids]):
        logger.debug(
            f"No query parameters provided, selected {len(raman_files)} of {len(raman_files)}."
        )
        return raman_files

    _pre_selected_samples = {i.sample.id for i in raman_files}
    rf_selection_index = []
    if select_sample_groups:
        raman_files_groups = list(
            filter(lambda x: x.sample.group in select_sample_groups, raman_files)
        )
        _pre_selected_samples = {i.sample.id for i in raman_files_groups}
        rf_selection_index += raman_files_groups

    if select_sample_ids:
        selected_sample_ids = list(
            filter(lambda x: x in select_sample_ids, _pre_selected_samples)
        )
        raman_files_samples = list(
            filter(lambda x: x.sample.id in selected_sample_ids, raman_files)
        )
        rf_selection_index += raman_files_samples

    selection = rf_selection_index
    logger.debug(f"Selected {len(selection)} of {len(raman_files)}.")

    if not selection:
        logger.info("Selection was empty.")

    return selection


def group_by_sample_group(index: Sequence[RamanFileInfo]):
    """Generator for Sample Groups, yields the name of group and group of the index SampleGroup"""
    return groupby(index, key=lambda x: x.sample.group)


def group_by_sample_id(index: Sequence[RamanFileInfo]):
    """Generator for SampleIDs, yields the name of group, name of SampleID and group of the index of the SampleID"""
    return groupby(index, key=lambda x: x.sample.id)


def iterate_over_groups_and_sample_id(index: Sequence[RamanFileInfo]):
    for grp_name, grp in group_by_sample_group(index):
        for sample_id, sgrp in group_by_sample_group(grp):
            yield grp_name, grp, sample_id, sgrp


def select_index_by_sample_groups(index: RamanFileInfoSet, sample_groups: list[str]):
    return filter(lambda x: x.sample.group in sample_groups, index)


def select_index_by_sample_ids(index: RamanFileInfoSet, sample_ids: list[str]):
    return filter(lambda x: x.sample.id in sample_ids, index)


def select_index(
    index: RamanFileInfoSet, sample_groups: list[str], sample_ids: list[str]
):
    group_selection = list(select_index_by_sample_groups(index, sample_groups))
    sample_selection = list(select_index_by_sample_ids(index, sample_ids))
    selection = group_selection + sample_selection
    return selection
