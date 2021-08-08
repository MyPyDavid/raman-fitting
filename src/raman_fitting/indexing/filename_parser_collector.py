"""
Created on Sun Aug  8 18:20:20 2021

@author: DW
"""
from pathlib import Path
from typing import List, Collection
import logging

logger = logging.getLogger(__name__)

from .filename_parser import PathParser


def make_collection(raman_files: Collection, **kwargs) -> List[PathParser]:

    pp_collection = []
    # _error_parse_filenames
    for file in raman_files:
        try:
            pp_res = PathParser(file, **kwargs)
            pp_collection.append(pp_res)
        except Exception as e:
            logger.warning(
                f"{__name__} make_collection unexpected error for calling PathParser on\n{file}.\n{e}"
            )
            # .append(file)
    pp_collection = sorted(pp_collection)
    return pp_collection
    # self.pp_collection = pp_collection
