from typing import List, Optional
from typing_extensions import Annotated

from pathlib import Path
from enum import StrEnum, auto
from loguru import logger
from raman_fitting.config.path_settings import RunModes
from raman_fitting.delegating.main_delegator import MainDelegator
from raman_fitting.imports.files.file_indexer import initialize_index_from_source_files
from .utils import get_package_version

import typer


class MakeTypes(StrEnum):
    INDEX = auto()
    CONFIG = auto()
    EXAMPLE = auto()


__version__ = "0.1.0"


def version_callback(value: bool):
    if value:
        package_version = get_package_version()
        typer_cli_version = f"Awesome Typer CLI Version: {__version__}"
        print(f"{package_version}\n{typer_cli_version}")
        raise typer.Exit()


app = typer.Typer()
state = {"verbose": False}


@app.command()
def run(
    models: Annotated[
        List[str],
        typer.Option(
            default_factory=list, help="Selection of models to use for deconvolution."
        ),
    ],
    sample_ids: Annotated[
        List[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of SampleIDs from index to run over.",
        ),
    ],
    group_ids: Annotated[
        List[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of sample groups from index to run over.",
        ),
    ],
    fit_models: Annotated[
        List[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of the composite LMfit models to use for fitting.",
        ),
    ],
    run_mode: Annotated[RunModes, typer.Argument()] = RunModes.NORMAL,
    multiprocessing: Annotated[bool, typer.Option("--multiprocessing")] = False,
):
    if run_mode is None:
        print("No make run mode passed")
        raise typer.Exit()
    kwargs = {"run_mode": run_mode, "use_multiprocessing": multiprocessing}
    if run_mode == RunModes.EXAMPLES:
        kwargs.update({"fit_model_specific_names": ["2peaks", "3peaks", "4peaks"]})
    logger.info(f"Starting raman_fitting with CLI args:\n{run_mode}")
    _main_run = MainDelegator(**kwargs)


@app.command()
def make(
    source_files: Annotated[List[Path], typer.Option()],
    index_file: Annotated[List[Path], typer.Option()],
    force_reindex: Annotated[bool, typer.Option("--force-reindex")] = False,
    make_type: Annotated[MakeTypes, typer.Option()] = None,
):
    if make_type is None:
        print("No make type args passed")
        raise typer.Exit()

    if make_type == MakeTypes.INDEX:
        initialize_index_from_source_files(
            files=source_files, index_file=index_file, force_reindex=force_reindex
        )

    elif make_type == MakeTypes.CONFIG:
        pass  # make config


@app.callback()
def main(
    verbose: bool = False,
    version: Annotated[
        Optional[bool], typer.Option("--version", callback=version_callback)
    ] = None,
):
    """
    Manage raman_fitting in the awesome CLI app.
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


if __name__ == "__main__":
    app()
