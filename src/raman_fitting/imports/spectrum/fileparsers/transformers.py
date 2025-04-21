from typing import Any

import tablib
from loguru import logger

from tablib import Dataset

from raman_fitting.imports.spectrum.fileparsers.column_headers import SpectrumDataKeys


def cast_rows_to_floats(
    data: Dataset,
) -> tuple[Dataset, list[tuple[int, list[str], Any]]]:
    filtered_data = Dataset()
    filtered_data.headers = data.headers
    errors = []
    for n, row in enumerate(data):
        try:
            digits_row = tuple(map(float, row))
        except (ValueError, TypeError) as e:
            errors.append((n, row, e))
            continue

        if not any(i is None for i in digits_row):
            filtered_data.append(digits_row)
    return filtered_data, errors


def split_single_rows_into_columns_by_header_keys(
    dataset: Dataset,
    header_keys: list[SpectrumDataKeys],
    sep=None,
    maxsplit=-1,
    raise_errors=False,
) -> Dataset:
    # Validate the dataset width
    if dataset.width != 1:
        raise ValueError(f"Dataset width should be 1, not {dataset.width}.")
    if len(header_keys) < 2:
        raise ValueError(f"Header keys should be at least 2, not {len(header_keys)}.")

    # Create a new dataset with the specified headers
    new_dataset = tablib.Dataset()
    new_dataset.headers = header_keys

    # Initialize a counter for ignored rows
    ignored_rows = []

    # Loop over each row in the dataset
    for row in dataset.get_col(0):
        split_row = row.split(sep=sep, maxsplit=maxsplit)

        # Check if the split row matches the expected number of columns
        if len(split_row) == len(header_keys):
            new_dataset.append(split_row)
        elif raise_errors:
            raise ValueError(
                "All rows must split into the same number of columns or use filter_errors=True."
            )
        else:
            ignored_rows += row

    # Log the number of ignored rows if filtering errors
    if ignored_rows:
        logger.debug(f"Ignored rows {ignored_rows} due to splitting errors.")

    return new_dataset
