""" this module prepares the local file paths for data and results"""

from typing import Dict
import logging
import sys
from pathlib import Path

# from .. import __package_name__

logger = logging.getLogger(__name__)

from raman_fitting.config import filepath_settings as config

#%%


def get_directory_paths_for_run_mode(run_mode: str = "", **kwargs) -> Dict:
    """
    Parameters
    ----------
    run_mode : str, optional
        this is name of the run mode. The default is ''.
    **kwargs : TYPE
        kwargs can contain keys such as DATASET_DIR to overwrite the standard config paths.

    Returns
    -------
    dest_dirs : dict
        dict containing 3 keys [RESULTS_DIR, DATASET_DIR, INDEX_FILE]

    """
    dest_dirs = {}
    DATASET_DIR = None
    RESULTS_DIR = None

    if run_mode in ("DEBUG", "testing"):
        # self.debug = True
        RESULTS_DIR = config.TESTS_RESULTS_DIR
        DATASET_DIR = config.TESTS_DATASET_DIR

    elif run_mode == "make_examples":
        RESULTS_DIR = config.PACKAGE_HOME.joinpath("example_results")
        DATASET_DIR = config.TESTS_DATASET_DIR
        # self._kwargs.update({'default_selection' : 'all'})

    elif run_mode in ("normal", "make_index"):
        RESULTS_DIR = config.RESULTS_DIR
        DATASET_DIR = config.DATASET_DIR
        # INDEX_FILE = config.INDEX_FILE
    else:
        logger.warning(f"Run mode {run_mode} not recognized. Exiting...")

    INDEX_FILE = RESULTS_DIR / config.INDEX_FILE_NAME
    DB_FILE = RESULTS_DIR / config.DB_FILE_NAME

    dest_dirs = {
        "RESULTS_DIR": Path(RESULTS_DIR),
        "DATASET_DIR": Path(DATASET_DIR),
        "INDEX_FILE": Path(INDEX_FILE),
        "DB_FILE": Path(DB_FILE),
    }

    if kwargs:
        dest_dirs = override_from_kwargs(dest_dirs, **kwargs)

    check_and_make_dirs(dest_dirs)

    return dest_dirs


def check_and_make_dirs(dest_dirs: dict = {}):
    DATASET_DIR = dest_dirs.get("DATASET_DIR", None)
    if DATASET_DIR:
        create_dataset_dir(DATASET_DIR)
    else:
        logger.warning(f"No datafiles directory was set for . Exiting...")

    RESULTS_DIR = dest_dirs.get("RESULTS_DIR", None)
    if RESULTS_DIR:
        if not RESULTS_DIR.is_dir():
            RESULTS_DIR.mkdir(exist_ok=True, parents=True)
            logger.info(
                f"check_and_make_dirs the results directory did not exist and was created at:\n{RESULTS_DIR}\n"
            )
    """ returns index file path """


def override_from_kwargs(_dict, **kwargs):
    _kwargs = kwargs
    if _kwargs:
        _keys = [i for i in _dict.keys() if i in _kwargs.keys()]
        _new_dict = {
            k: Path(val) if not _kwargs.get(k, None) else _kwargs[k]
            for k, val in _dict.items()
        }
        if _new_dict != _dict:
            logger.debug(f"override_from_kwargs keys {_keys} were overwritten")
        return _new_dict
    else:
        return _dict


def create_dataset_dir(DATASET_DIR):  # pragma: no cover
    if not DATASET_DIR.is_dir():
        logger.warning(
            f"The datafiles directory does not exist yet, the program will now try to create this folder.\n{DATASET_DIR}"
            # therefore {config.__package_name__} can not find any files.
            # The program will now try to create this folder.
        )
        try:
            DATASET_DIR.mkdir()
            logger.warning(
                f"""The datafiles directory has now been created at:
{DATASET_DIR}
please place your raman datafiles in this folder and run {config.__package_name__} again.
{config.__package_name__} exits now.
"""
            )
            sys.exit()
            # IDEA build in daemon version with folder watcher....
        except Exception as exc:
            logger.warning(
                f"""The datafiles directory could not be created at:
{DATASET_DIR}
An unexpected error ocurred:
{exc}
please redefine the path for dataset_dir in the config settings.
"""
            )
    else:
        # Check if dir is not empty else raise a warning
        _diter = DATASET_DIR.iterdir()
        try:
            next(_diter)
        except StopIteration:
            logger.warning(
                f"""The datafiles directory is empty:
{DATASET_DIR}
please place your files in here or
change this path in the config settings.
"""
            )
