from typing import Sequence
from pathlib import Path

import numpy as np
from tablib import Dataset

from loguru import logger


def filter_data_for_numeric(data: Dataset):
    filtered_data = Dataset()
    filtered_data.headers = data.headers

    for row in data:
        try:
            digits_row = tuple(map(float, row))
        except ValueError:
            continue
        except TypeError:
            continue

        if not any(i is None for i in digits_row):
            filtered_data.append(digits_row)
    return filtered_data


def load_dataset_from_file(filepath, **kwargs) -> Dataset:
    with open(filepath, "r") as fh:
        imported_data = Dataset(**kwargs).load(fh)
    return imported_data


def check_header_keys(dataset: Dataset, header_keys: Sequence[str]):
    if set(header_keys) not in set(dataset.headers):
        first_row = list(dataset.headers)
        dataset.insert(0, first_row)
        dataset.headers = header_keys
    return dataset


def read_file_with_tablib(
    filepath: Path, header_keys: Sequence[str], sort_by=None
) -> Dataset:
    data = load_dataset_from_file(filepath)
    data = check_header_keys(data, header_keys)
    numeric_data = filter_data_for_numeric(data)
    sort_by = header_keys[0] if sort_by is None else sort_by
    sorted_data = numeric_data.sort(sort_by)
    return sorted_data


def read_text(filepath, max_bytes=10**6, encoding="utf-8", errors=None):
    """additional read text method for raw text data inspection"""
    _text = "read_text_method"
    filesize = filepath.stat().st_size
    if filesize < max_bytes:
        try:
            _text = filepath.read_text(encoding=encoding, errors=errors)
            # _text.splitlines()
        except Exception as exc:
            # IDEA specify which Exceptions are expected
            _text += "\nread_error"
            logger.warning(f"file read text error => skipped.\n{exc}")
    else:
        _text += "\nfile_too_large"
        logger.warning(f" file too large ({filesize})=> skipped")

    return _text


def use_np_loadtxt(filepath, usecols=(0, 1), **kwargs) -> np.array:
    array = np.array([])
    try:
        array = np.loadtxt(filepath, usecols=usecols, **kwargs)
    except IndexError:
        logger.debug(f"IndexError called np genfromtxt for {filepath}")
        array = np.genfromtxt(filepath, invalid_raise=False)
    except ValueError:
        logger.debug(f"ValueError called np genfromtxt for {filepath}")
        array = np.genfromtxt(filepath, invalid_raise=False)
    except Exception as exc:
        _msg = f"Can not load data from txt file: {filepath}\n{exc}"
        logger.error(_msg)
        raise ValueError(_msg) from exc
    return array
