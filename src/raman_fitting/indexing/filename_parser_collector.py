"""
Created on Sun Aug  8 18:20:20 2021

@author: DW
"""
from typing import List, Collection
import logging

from .filename_parser import PathParser

logger = logging.getLogger(__name__)


def make_collection(raman_files: Collection, **kwargs) -> List[PathParser]:
    pp_collection = []
    for file in raman_files:
        try:
            pp_res = PathParser(file, **kwargs)
            pp_collection.append(pp_res)
        except Exception as e:
            logger.warning(
                f"{__name__} make_collection unexpected error for calling PathParser on\n{file}.\n{e}"
            )
    pp_collection = sorted(pp_collection)
    return pp_collection
