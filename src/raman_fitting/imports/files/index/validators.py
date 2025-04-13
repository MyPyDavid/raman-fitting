from pathlib import Path

from raman_fitting.imports.files.exceptions import IndexValidationError
from raman_fitting.imports.files.models import RamanFileInfoSet

from tablib import Dataset
from loguru import logger


def validate_dataset_headers(dataset_rf: Dataset, index_dataset: Dataset) -> None:
    if dataset_rf.headers != index_dataset.headers:
        raise IndexValidationError("Headers are different.")


def validate_dataset_length(dataset_rf: Dataset, index_dataset: Dataset) -> None:
    if len(dataset_rf) != len(index_dataset):
        raise IndexValidationError("Length of datasets are different.")


def validate_dataset_rows(dataset_rf: Dataset, index_dataset: Dataset) -> None:
    _errors = []
    for row1, row2 in zip(dataset_rf.dict, index_dataset.dict):
        if row1 != row2:
            _errors.append(f"Row1: {row1} != Row2: {row2}")
    if _errors:
        raise IndexValidationError(f"Errors: {_errors}")


def validate_and_set_dataset(
    index_dataset: Dataset, raman_files: RamanFileInfoSet
) -> None:
    if index_dataset is None:
        if raman_files is None:
            raise IndexValidationError(
                "Index error, No dataset or raman_files provided."
            )
        elif not raman_files:
            raise IndexValidationError(
                "Index error, raman_files is empty and dataset not provided"
            )
        return

    if not raman_files:
        return  # can not compare if raman_files is empty

    dataset_rf = raman_files.cast_to_dataset()
    if dataset_rf is not None:
        validate_dataset_headers(dataset_rf, index_dataset)
        validate_dataset_length(dataset_rf, index_dataset)
        validate_dataset_rows(dataset_rf, index_dataset)


def validate_index_file_path(index_file: Path | None, force_reindex: bool) -> bool:
    if index_file is None:
        logger.debug(
            "Index file not provided, index will not be reloaded or persisted."
        )
        return False

    if index_file.exists() and not force_reindex:
        return True
    elif force_reindex:
        logger.warning(
            f"Index index_file file {index_file} exists and will be overwritten."
        )
    else:
        logger.info(
            "Index index_file file does not exists but was asked to reload from it."
        )
    return False
