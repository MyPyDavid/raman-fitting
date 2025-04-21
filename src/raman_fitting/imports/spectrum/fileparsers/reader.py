from pathlib import Path

from loguru import logger
from tablib import Dataset

from raman_fitting.imports.errors import FileProcessingError, ErrorType
from raman_fitting.imports.spectrum.fileparsers.column_headers import (
    SpectrumDataKeys,
    DEFAULT_SORT_BY_DATA_KEY,
)
from raman_fitting.imports.spectrum.fileparsers.columns import (
    transform_dataset_to_columns_with_header_keys,
)
from raman_fitting.imports.spectrum.fileparsers.rows import (
    validate_numeric_data_in_dataset_from_file,
    check_if_header_is_also_a_row_of_data,
    check_header_keys_are_in_rows,
)
from raman_fitting.imports.spectrum.fileparsers.transformers import cast_rows_to_floats
from raman_fitting.utils.loaders import load_dataset_from_file


def read_file_with_tablib(
    filepath: Path,
    header_keys: list[SpectrumDataKeys],
    sort_by_key: str | None = DEFAULT_SORT_BY_DATA_KEY,
) -> Dataset | FileProcessingError:
    try:
        data = load_dataset_from_file(filepath)
    except FileNotFoundError as e:
        logger.error(f"File not found {filepath}: {e}")
        return FileProcessingError(filepath, ErrorType.FILE_NOT_FOUND, e)

    try:
        # check if there is any data at all
        data[0]
    except IndexError as e:
        logger.error(f"This file {filepath} does not contain any data.")
        return FileProcessingError(filepath, ErrorType.NO_VALID_DATA, e)

    try:
        # validates with VALID_MIN_ROWS
        validate_numeric_data_in_dataset_from_file(data)
    except ValueError as e:
        return FileProcessingError(filepath, ErrorType.NO_VALID_DATA, e)

    if check_if_header_is_also_a_row_of_data(data):
        # insert the 0th row from headers to the data
        data.insert(0, data.headers)
        data.headers = [f"{n}: {i}" for n, i in enumerate(data.headers)]

    if data.width != len(header_keys):
        data = transform_dataset_to_columns_with_header_keys(data, header_keys)

    if set(data.headers) < set(header_keys):
        missing_keys = set(header_keys) - set(data.headers)
        return FileProcessingError(
            filepath,
            ErrorType.NO_VALID_DATA,
            ("Header keys are missing from data headers" f"{missing_keys}"),
        )

    try:
        check_header_keys_are_in_rows(data, header_keys)
    except ValueError as e:
        return FileProcessingError(
            filepath,
            ErrorType.NO_VALID_DATA,
            e,
        )

    floats_casted_data, casting_errors = cast_rows_to_floats(data)
    if casting_errors:
        if len(casting_errors) > len(floats_casted_data):
            logger.error(
                f"Many rows({len(casting_errors)}) could not be casted to floats."
            )
        else:
            logger.info(
                f"Some rows({len(casting_errors)}) could not be casted to floats."
            )
        if not floats_casted_data:
            return FileProcessingError(
                filepath,
                ErrorType.NO_VALID_DATA,
                "Could not cast any of the rows to floats.",
            )

    sort_by_key = sort_by_key or DEFAULT_SORT_BY_DATA_KEY

    if sort_by_key not in floats_casted_data.headers:
        return FileProcessingError(
            filepath,
            ErrorType.NO_VALID_DATA,
            f"Sorting key {sort_by_key} not in data headers {floats_casted_data.headers}.",
        )

    floats_casted_data = floats_casted_data.sort(sort_by_key)

    return floats_casted_data
