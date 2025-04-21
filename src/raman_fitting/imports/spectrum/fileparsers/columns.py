from typing import Sequence

import tablib
from loguru import logger
from tablib import Dataset

from raman_fitting.imports.spectrum.fileparsers.column_headers import SpectrumDataKeys
from raman_fitting.imports.spectrum.fileparsers.transformers import (
    split_single_rows_into_columns_by_header_keys,
)


def transform_dataset_to_columns_with_header_keys(
    data: Dataset, header_keys: list[SpectrumDataKeys]
) -> Dataset:
    if data.width < len(header_keys):
        logger.warning(
            f"data has only a single columns {data.width}, splitting into {len(header_keys)}: {', '.join([i.value for i in header_keys])}"
        )
        return split_single_rows_into_columns_by_header_keys(data, header_keys)

    else:
        # if dataset.width > len(header_keys)
        logger.warning(
            f"data has too many columns {data.width}, taking first {len(header_keys)}"
        )
        return select_columns_from_data_by_header_keys(data, header_keys)


def select_columns_from_data_by_header_keys(
    data: Dataset, header_keys: Sequence[str]
) -> Dataset:
    header_keys_in_dataset = [i for i in header_keys if i in data.headers]
    excluded_headers = [i for i in header_keys if i not in data.headers]

    new_dataset = tablib.Dataset()
    new_dataset.headers = header_keys
    for n, i in enumerate(header_keys_in_dataset):
        new_dataset.append_col(data.get_col(n), header=i)

    logger.debug(
        f"Selected columns {header_keys} from dataset of len {len(data)}, ignored {', '.join(excluded_headers)}"
    )
    return new_dataset
