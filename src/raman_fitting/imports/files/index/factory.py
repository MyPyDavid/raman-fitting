from pathlib import Path
from typing import Sequence

from raman_fitting.imports.files.file_finder import FileFinder
from raman_fitting.imports.files.collectors import (
    collect_raman_file_index_info_from_files,
)
from raman_fitting.imports.files.index.models import RamanFileIndex

from loguru import logger


def initialize_index_from_source_files(
    files: Sequence[Path] | None = None,
    index_file: Path | None = None,
    force_reindex: bool = False,
    persist_to_file: bool = False,
) -> RamanFileIndex:
    raman_files = collect_raman_file_index_info_from_files(raman_files=files)
    if not raman_files:
        logger.warning("No raman files were found.")
        return RamanFileIndex(raman_files=None, index_file=None)

    raman_index = RamanFileIndex(
        index_file=index_file,
        raman_files=raman_files,
        force_reindex=force_reindex,
        persist_to_file=persist_to_file,
    )
    if len(raman_index) == 0:
        logger.warning("Index is empty, no raman files were found.")
    else:
        logger.info(f"index prepared with len {len(raman_index)}")
    # read_or_load_data(raman_index)  # Directly call read_or_load_data
    return raman_index


def find_files_and_initialize_index(
    directory: Path,
    suffixes: Sequence[str],
    exclusions: Sequence[str],
    index_file: Path,
    persist_to_file: bool = False,
) -> RamanFileIndex:
    file_finder = FileFinder(
        directory=directory,
        suffixes=suffixes,
        exclusions=exclusions,
    )
    return initialize_index_from_source_files(
        files=file_finder.files,
        index_file=index_file,
        force_reindex=True,
        persist_to_file=persist_to_file,
    )


def get_or_create_index(
    index: RamanFileIndex | Path | None,
    directory: Path | None = None,
    suffixes: Sequence[str] = (),
    exclusions: Sequence[str] = (),
    index_file: Path | None = None,
    force_reindex: bool = False,
    persist_index: bool = False,
) -> RamanFileIndex:
    if index is None and directory is not None:
        return find_files_and_initialize_index(
            directory=directory,
            suffixes=suffixes,
            exclusions=exclusions,
            index_file=index_file,
            persist_to_file=persist_index,
        )

    elif isinstance(index, Path):
        return initialize_index_from_source_files(
            index_file=index, force_reindex=force_reindex, persist_to_file=persist_index
        )
    elif isinstance(index, RamanFileIndex):
        return index
    else:
        raise TypeError(f"can not handle index of type {type(index)} ")
