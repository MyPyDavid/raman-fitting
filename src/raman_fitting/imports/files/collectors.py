"""
Asynchronous file collection and processing for Raman spectroscopy files.

Created: 2025-04-18 12:14:13
Author: MyPyDavid
"""

from pathlib import Path
from typing import List, Collection, Sequence
import logging
import asyncio
import sys
from functools import partial

from raman_fitting.imports.files.models import RamanFileInfo, RamanFileInfoSet
from raman_fitting.imports.spectrum.datafile_parsers import SPECTRUM_FILETYPE_PARSERS

logger = logging.getLogger(__name__)


async def resolve_path(path: Path) -> Path:
    """Asynchronously resolve a path using a thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, path.resolve)


async def is_file(path: Path) -> bool:
    """Asynchronously check if path is a file."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, path.is_file)


async def is_dir(path: Path) -> bool:
    """Asynchronously check if path is a directory."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, path.is_dir)


async def collect_files_from_dir(directory: Path, suffix: str) -> List[Path]:
    """Asynchronously collect files with given suffix from directory."""
    loop = asyncio.get_running_loop()
    glob_pattern = f"*.{suffix}"
    rglob_func = partial(list, directory.rglob(glob_pattern))
    return await loop.run_in_executor(None, rglob_func)


async def process_single_path(file: Path, suffixes: List[str]) -> List[Path]:
    """Process a single path, either file or directory."""
    resolved_file = await resolve_path(file)

    if await is_file(resolved_file):
        return [resolved_file]
    elif await is_dir(resolved_file):
        tasks = [collect_files_from_dir(resolved_file, suffix) for suffix in suffixes]
        results = await asyncio.gather(*tasks)
        return [item for sublist in results for item in sublist]
    return []


async def collect_valid_files(raman_files: Collection[Path]) -> List[Path]:
    """
    Asynchronously collects valid files from the given collection of paths.

    Args:
        raman_files: Collection of Path objects to process

    Returns:
        List of resolved valid file paths
    """
    if not raman_files:
        return []

    suffixes = [i.lstrip(".") for i in SPECTRUM_FILETYPE_PARSERS.keys()]
    tasks = [process_single_path(file, suffixes) for file in raman_files]
    results = await asyncio.gather(*tasks)

    # Flatten results
    return [item for sublist in results for item in sublist]


async def create_raman_file_info(
    file: Path,
) -> tuple[RamanFileInfo | None, dict | None]:
    """Asynchronously create a RamanFileInfo object from a file."""
    try:
        loop = asyncio.get_running_loop()
        info = await loop.run_in_executor(None, lambda: RamanFileInfo(filepath=file))
        return info, None
    except Exception as exc:
        logger.warning(
            f"{__name__} create_raman_file_info unexpected error for calling RamanFileInfo on\n"
            f"{file}.\n{exc}"
        )
        return None, {"file": file, "error": exc}


async def create_raman_file_info_set(valid_files: List[Path]) -> RamanFileInfoSet:
    """
    Asynchronously creates a RamanFileInfoSet from the given list of valid files.

    Args:
        valid_files: List of validated file paths

    Returns:
        RamanFileInfoSet containing the processed files
    """
    if not valid_files:
        return RamanFileInfoSet(raman_files=[])

    tasks = [create_raman_file_info(file) for file in valid_files]
    results = await asyncio.gather(*tasks)

    pp_collection = []
    failed_files = []

    for info, error in results:
        if info is not None:
            pp_collection.append(info)
        if error is not None:
            failed_files.append(error)

    if failed_files:
        logger.warning(
            f"{__name__} create_raman_file_info_set failed for {len(failed_files)} files."
        )

    return RamanFileInfoSet(raman_files=pp_collection)


async def collect_raman_file_index_info_from_files_async(
    raman_files: Sequence[Path],
) -> RamanFileInfoSet | None:
    """
    Asynchronously collects RamanFileInfoSet from the given sequence of paths.

    Args:
        raman_files: Sequence of paths to process

    Returns:
        RamanFileInfoSet if successful, None otherwise
    """
    if not raman_files:
        return None

    valid_files = await collect_valid_files(raman_files)
    if not valid_files:
        logger.warning("No valid files found.")
        return None

    raman_file_info_set = await create_raman_file_info_set(valid_files)
    logger.info(
        f"Successfully created index with {len(raman_file_info_set)} entries "
        f"from {len(valid_files)} files."
    )
    return raman_file_info_set


def collect_raman_file_index_info_from_files(
    raman_files: Sequence[Path],
) -> RamanFileInfoSet | None:
    """
    Synchronous wrapper for backward compatibility.

    This function maintains the original API while using async implementation
    internally. Compatible with Python 3.10+.
    """
    if not raman_files:
        return None

    if sys.version_info >= (3, 11):
        return asyncio.run(collect_raman_file_index_info_from_files_async(raman_files))
    else:
        # Python 3.10 compatibility
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                collect_raman_file_index_info_from_files_async(raman_files)
            )
        finally:
            loop.close()
            asyncio.set_event_loop(None)


# Example usage with proper error handling:
if __name__ == "__main__":
    import time

    async def main():
        try:
            # Example paths
            paths = [Path("path/to/files")]

            # Async version
            start = time.time()
            _result = await collect_raman_file_index_info_from_files_async(paths)
            print(f"Async took {time.time() - start:.2f} seconds")

            # Sync version (for comparison)
            start = time.time()
            _result_sync = collect_raman_file_index_info_from_files(paths)
            print(f"Sync took {time.time() - start:.2f} seconds")

        except Exception as e:
            logger.error(f"Error in main: {e}")
            raise

    if sys.version_info >= (3, 11):
        asyncio.run(main())
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()
            asyncio.set_event_loop(None)
