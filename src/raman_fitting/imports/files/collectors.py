from pathlib import Path
from typing import List, Collection, Sequence
import logging

from raman_fitting.imports.files.models import RamanFileInfo, RamanFileInfoSet
from raman_fitting.imports.spectrum.datafile_parsers import SPECTRUM_FILETYPE_PARSERS

logger = logging.getLogger(__name__)


def collect_valid_files(raman_files: Collection[Path]) -> List[Path]:
    """Collects valid files from the given collection of paths."""
    valid_files = []
    for file in raman_files:
        resolved_file = file.resolve()
        if resolved_file.is_file():
            valid_files.append(resolved_file)
        elif resolved_file.is_dir():
            suffixes = [i.lstrip(".") for i in SPECTRUM_FILETYPE_PARSERS.keys()]
            for suffix in suffixes:
                valid_files.extend(resolved_file.rglob(f"*.{suffix}"))
    return valid_files


def create_raman_file_info_set(valid_files: List[Path]) -> RamanFileInfoSet:
    """Creates a RamanFileInfoSet from the given list of valid files."""
    pp_collection = []
    failed_files = []
    for file in valid_files:
        try:
            pp_res = RamanFileInfo(file=file)
            pp_collection.append(pp_res)
        except Exception as exc:
            logger.warning(
                f"{__name__} create_raman_file_info_set unexpected error for calling RamanFileInfo on\n{file}.\n{exc}"
            )
            failed_files.append({"file": file, "error": exc})

    if failed_files:
        logger.warning(
            f"{__name__} create_raman_file_info_set failed for {len(failed_files)} files."
        )

    return RamanFileInfoSet(raman_files=pp_collection)


def collect_raman_file_index_info_from_files(
    raman_files: Sequence[Path],
) -> RamanFileInfoSet | None:
    """Collects RamanFileInfoSet from the given sequence of paths."""
    if not raman_files:
        return None

    valid_files = collect_valid_files(raman_files)
    if not valid_files:
        logger.warning("No valid files found.")
        return None

    raman_file_info_set = create_raman_file_info_set(valid_files)
    logger.info(
        f"Successfully created index with {len(raman_file_info_set)} entries from {len(valid_files)} files."
    )
    return raman_file_info_set
