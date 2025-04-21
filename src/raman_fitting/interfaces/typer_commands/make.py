from typing_extensions import Annotated
from pathlib import Path
from enum import auto

from raman_fitting.utils.compat import StrEnum
from raman_fitting.config.load_config_from_toml import dump_default_config
from raman_fitting.config.path_settings import INDEX_FILE_NAME
from raman_fitting.imports.files.file_finder import FileFinder
from raman_fitting.imports.files.index.factory import initialize_index_from_source_files
from raman_fitting.imports.spectrum.fileparsers.filetypes import (
    SPECTRUM_FILETYPE_PARSERS,
)

import typer

LOCAL_INDEX_FILE = Path.cwd().joinpath(INDEX_FILE_NAME)
LOCAL_CONFIG_FILE = Path.cwd().joinpath("raman_fitting.toml")

make_app = typer.Typer()


class MakeTypes(StrEnum):
    INDEX = auto()
    CONFIG = auto()
    EXAMPLE = auto()


def current_dir_prepare_index_kwargs() -> tuple[list[Path], Path]:
    file_finder = FileFinder(
        directory=Path.cwd(),
        suffixes=list(SPECTRUM_FILETYPE_PARSERS.keys()),
        exclusions=["."],
    )
    source_files = file_finder.files
    index_file = LOCAL_INDEX_FILE
    return source_files, index_file


@make_app.command()
def index(
    source_files: Annotated[list[Path] | None, typer.Option()] = None,
    index_file: Annotated[Path | None, typer.Option()] = None,
    force_reindex: Annotated[bool, typer.Option("--force-reindex")] = False,
):
    """Create or update the index."""
    if index_file is not None:
        index_file = index_file.resolve()

    if not source_files:
        source_files, index_file = current_dir_prepare_index_kwargs()

    index = initialize_index_from_source_files(
        files=source_files,
        index_file=index_file,
        force_reindex=force_reindex,
        persist_to_file=True,
    )
    if index is not None:
        typer.echo(
            f"Index({len(index)}) is initialized and saved to {index.index_file}"
        )
    else:
        typer.echo("Index could not be initialized. Check source files.")


@make_app.command()
def config():
    """Create the default configuration file."""
    dump_default_config(LOCAL_CONFIG_FILE)
    typer.echo(f"Config file created: {LOCAL_CONFIG_FILE}")


@make_app.command()
def example():
    """Create example files or configurations."""
    # Add logic to create example files or configurations
    typer.echo("Example files or configurations created.")


if __name__ == "__main__":
    make_app()
