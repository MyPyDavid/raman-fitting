from pathlib import Path
from typing import List, Collection
import logging

from .models import RamanFileInfo

logger = logging.getLogger(__name__)


def collect_raman_file_infos(
    raman_files: Collection[Path], **kwargs
) -> List[RamanFileInfo]:
    pp_collection = []
    # _extra_assign_destdir_and_set_paths(index)
    for file in raman_files:
        try:
            pp_res = RamanFileInfo(**{"file": file})
            pp_collection.append(pp_res)
        except Exception as exc:
            raise exc from exc
            logger.warning(
                f"{__name__} collect_raman_file_infos unexpected error for calling RamanFileInfo on\n{file}.\n{exc}"
            )
    # pp_collection = sorted(pp_collection)
    return pp_collection
