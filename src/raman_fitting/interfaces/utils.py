from pathlib import Path
from typing import List

import typer

from raman_fitting.imports.files.file_finder import FileFinder
from raman_fitting.imports.spectrum.fileparsers.filetypes import (
    SPECTRUM_FILETYPE_PARSERS,
)
from raman_fitting.config.path_settings import LOCAL_INDEX_FILE
from raman_fitting.interfaces import __version__


def get_package_version() -> str:
    try:
        import importlib.metadata

        _version = importlib.metadata.version("raman_fitting")
    except ImportError:
        _version = "version.not.found"

    _version_text = f"raman_fitting version: {_version}"
    return _version_text


def current_dir_prepare_index_kwargs() -> tuple[List[Path], Path]:
    file_finder = FileFinder(
        directory=Path.cwd(),
        suffixes=list(SPECTRUM_FILETYPE_PARSERS.keys()),
        exclusions=["."],
    )
    source_files = file_finder.files
    index_file = LOCAL_INDEX_FILE
    return source_files, index_file


def version_callback(value: bool):
    if value:
        package_version = get_package_version()
        typer_cli_version = f"Awesome Typer CLI Version: {__version__}"
        print(f"{package_version} {typer_cli_version}")
        raise typer.Exit()
