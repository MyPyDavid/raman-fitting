""" Indexer for raman data files """
import logging
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

from raman_fitting.config.filepath_helper import get_directory_paths_for_run_mode
from raman_fitting.imports.collector import collect_raman_file_infos

from .file_finder import find_files
from .index_funcs import load_index, index_selection

logger = logging.getLogger(__name__)
logger.propagate = False


class RamanFile(BaseModel):
    pass


class MakeRamanFilesIndex:
    """

    Finds the RAMAN files in the data folder from config and creates an overview, on the attribute .index
    finds a list of files,

    """

    debug = False

    table_name = "ramanfiles"

    def __init__(
        self, force_reload=True, run_mode="normal", dataset_dirs=None, **kwargs
    ):
        self._cqnm = self.__class__.__qualname__

        self._kwargs = kwargs
        self.force_reload = force_reload
        self.run_mode = run_mode

        if not dataset_dirs:
            dataset_dirs = get_directory_paths_for_run_mode(run_mode=self.run_mode)

        self.dataset_dirs = dataset_dirs
        for k, val in self.dataset_dirs.items():
            if isinstance(val, Path):
                setattr(self, k, val)

        self.raman_files = find_files(self.DATASET_DIR, suffixes=[".txt", ".csv"])
        self.index_file = dataset_dirs["INDEX_FILE"]
        self.index = pd.DataFrame()
        self._error_parse_filenames = []
        # if "normal" in run_mode and not self.debug and not self.force_reload:
        index = load_index(self.index_file, reload=self.force_reload)
        # breakpoint()
        if index is None:
            index = collect_raman_file_infos(self.raman_files, **self._kwargs)
        self.index = index
        self.index_selection = index_selection(self.index, **self._kwargs)

    def __repr__(self):
        if self.index is None:
            return f"{self._cqnm} with index (0)"
        return f"{self._cqnm} with index ({len(self.index)})"

    def __len__(self):
        if self.index is None:
            return 0
        return len(self.index)


def create_raman_file_index(raman_files, **kwargs):
    """loops over the files and scrapes the index data from each file"""

    index = collect_raman_file_infos(raman_files, kwargs)
    # breakpoint()
    # index = pd.DataFrame([i.parse_result for i in pp_collection])
    # index = _extra_assign_destdir_and_set_paths(index)
    logger.info(f"successfully made index {len(index)} from {len(raman_files)} files")
    if 0:
        logger.info(f"errors for filename parser from {len(raman_files)} files")
    return index


def main():
    """test run for indexer"""
    RamanIndex = None
    try:
        RamanIndex = MakeRamanFilesIndex(read_data=True, run_mode="make_examples")

    except Exception as e:
        logger.error(f"Raman Index error: {e}")
    return RamanIndex


if __name__ == "__main__":
    RamanIndex = main()
