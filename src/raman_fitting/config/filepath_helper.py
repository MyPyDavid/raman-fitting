""" this module prepares the local file paths for data and results"""

from typing import Dict
import logging

from pathlib import Path

import raman_fitting

logger = logging.getLogger(__name__)

from .filepath_settings import Config


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
    dataset_dir, results_dir = None, None

    run_mode_config = run_mode.lower()
    config_aliases = {"make_index": "normal"}
    if run_mode_config in config_aliases.keys():
        run_mode_config = config_aliases[run_mode_config]
    
    config = Config().CONFIG

    if run_mode_config in config.keys():
        dataset_dir = config[run_mode_config]["DATASET_DIR"]
        results_dir = config[run_mode_config]["RESULTS_DIR"]
    else:
        logger.warning(f"Run mode {run_mode} not recognized. Exiting...")

    index_file = config["defaults"]["USER_PACKAGE_HOME"] / config["defaults"]["INDEX_FILE_NAME"]

    dest_dirs = {
        "RESULTS_DIR": Path(results_dir),
        "DATASET_DIR": Path(dataset_dir),
        "INDEX_FILE": Path(index_file),
    }

    if kwargs:
        dest_dirs = override_from_kwargs(dest_dirs, **kwargs)

    check_and_make_dirs(dest_dirs['DATASET_DIR'], dest_dirs['RESULTS_DIR'])

    return dest_dirs


def check_and_make_dirs(dataset_dir: Path, results_dir: Path) -> None:
    
    create_dataset_dir(dataset_dir)

    if not results_dir.is_dir():
        results_dir.mkdir(exist_ok=True, parents=True)
        logger.info(
            f"check_and_make_dirs the results directory did not exist and was created at:\n{results_dir}\n"
        )


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
please place your raman datafiles in this folder and run {raman_fitting.__package_name__} again.
{raman_fitting.__package_name__} exits now.
"""
            )
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


def create_package_home_dir(package_home: Path):
    if package_home.is_dir():
        logger.info(
            f"Package home directory exists at:\n{package_home}\n--------------------"
        )
        return
    package_home_choice = input(
        f"""Package home directory did not exist, will now be created at:)
        {package_home}  
        --------------------
        Choose yes(y) to continue or no(n) to select your directory."""
    )
    if package_home_choice.startswith('n'):
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        package_home = Path(filedialog.askdirectory())

    try:
        logger.warning(
            f"Package home directory did not exist, will now be created at:\n{package_home}\n--------------------"
        )
        package_home.mkdir()
    except Exception as exc:
        logger.warning(
            f"Package home mkdir unexpected error\n{exc}.\nFolder{package_home} could not be created, exiting."
        )
        exit()

