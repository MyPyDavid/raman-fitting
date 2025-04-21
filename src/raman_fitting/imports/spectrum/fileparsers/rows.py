from statistics import mean

from loguru import logger
from tablib import Dataset

from raman_fitting.imports.spectrum.fileparsers.column_headers import SpectrumDataKeys


def validate_numeric_data_in_dataset_from_file(data: Dataset) -> Dataset | None:
    # introspect the data, basic numeric validation

    numeric_joined_per_row = [
        (n, "".join(a for i in row for a in i if a.isnumeric()))
        for n, row in enumerate(data)
    ]
    len_numeric_per_row = [len(i) for n, i in numeric_joined_per_row]
    if not len_numeric_per_row or mean(len_numeric_per_row) < VALID_MIN_ROWS:
        msg = f"There is nearly no numeric data in the rows:{''.join(map(str,len_numeric_per_row))}"
        logger.error(msg)
        raise ValueError("Insufficient numeric data")


def check_if_header_is_also_a_row_of_data(data: Dataset) -> bool:
    # introspect the data, basic numeric validation

    len_numeric_per_row = [
        len(list(a for i in row for a in i if a.isnumeric())) for row in data
    ]
    numeric_in_headers = [i for header in data.headers for i in header if i.isnumeric()]
    if numeric_in_headers and len_numeric_per_row:
        if len(numeric_in_headers) >= min(len_numeric_per_row):
            # if there are a lot of numeric characters in the header
            # then the header maybe also a row of data
            # so the header can be inserted as a row of data
            logger.debug("The header is also a row of data")
            return True

    return False


VALID_MIN_ROWS = 3


def check_header_keys_are_in_rows(
    data: Dataset, header_keys: list[SpectrumDataKeys]
) -> None:
    for row in data:
        if set(header_keys) in set(row):
            raise ValueError("Header keys in row")
