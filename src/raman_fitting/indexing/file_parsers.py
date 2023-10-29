import logging
from pathlib import Path

from warnings import warn
from typing import List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


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
        raise ValueError(_msg)
    return array


def cast_array_into_spectrum_frame(array, keys: List[str] = None) -> pd.DataFrame:
    """cast array into spectrum frame"""
    if not array.ndim == len(keys):
        raise ValueError(
            f"Array dimension {array.ndim} does not match the number of keys {len(keys)}"
        )

    try:
        spectrum_data = pd.DataFrame(
            array, columns=keys
        )
        return spectrum_data
    except Exception as exc:
        _msg = f"Can not create DataFrame from array object: {array}\n{exc}"
        logger.error(_msg)
        raise ValueError(_msg)


def load_spectrum_from_txt(filepath, **kwargs) -> pd.DataFrame:
    """load spectrum from txt file"""
    keys = kwargs.pop("keys")
    array = use_np_loadtxt(filepath, **kwargs)
    spectrum_data = cast_array_into_spectrum_frame(array, keys=keys)
    return spectrum_data
