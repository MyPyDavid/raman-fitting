from typing import Optional
from typing_extensions import Annotated
from pathlib import Path

from raman_fitting.config.load_config_from_toml import dump_default_config
from raman_fitting.config.path_settings import INDEX_FILE_NAME, RunModes
from raman_fitting.delegators.main_delegator import MainDelegator
from raman_fitting.imports.files.file_finder import FileFinder
from raman_fitting.imports.files.index.factory import initialize_index_from_source_files
from raman_fitting.imports.spectrum.fileparsers.filetypes import (
    SPECTRUM_FILETYPE_PARSERS,
)
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames

import typer
from rich.console import Console
import sys

LOCAL_INDEX_FILE = Path.cwd().joinpath(INDEX_FILE_NAME)
LOCAL_CONFIG_FILE = Path.cwd().joinpath("raman_fitting.toml")

console = Console()

run_app = typer.Typer()


def current_dir_prepare_index_kwargs() -> tuple[list[Path], Path]:
    file_finder = FileFinder(
        directory=Path.cwd(),
        suffixes=list(SPECTRUM_FILETYPE_PARSERS.keys()),
        exclusions=["."],
    )
    source_files = file_finder.files
    index_file = LOCAL_INDEX_FILE
    return source_files, index_file


def setup_logging(log_file: Optional[Path], log_level: str):
    from loguru import logger

    logger.enable("raman_fitting")
    logger.remove()  # Remove any existing handlers
    logger.add(sys.stderr, level=log_level)

    if log_file:
        log_file = Path(log_file).resolve()
        logger.add(log_file, level=log_level, rotation="10 MB")
    return logger


def run_command(
    models: Optional[list[str]] = None,
    sample_ids: Optional[list[str]] = None,
    group_ids: Optional[list[str]] = None,
    fit_models: Optional[list[str]] = None,
    run_mode: RunModes = RunModes.NORMAL,
    index_file: Optional[Path] = None,
    log_file: Optional[Path] = None,
    log_level: str = "INFO",
    **extra_kwargs,
):
    kwargs = {
        "run_mode": run_mode,
        "index": None,
        "fit_model_region_names": fit_models or RegionNames,
        "select_sample_ids": sample_ids,
        "select_sample_groups": group_ids,
        "selected_models": models,
    }
    kwargs.update(extra_kwargs)

    logger = setup_logging(log_file, log_level)

    if run_mode == RunModes.CURRENT_DIR:
        source_files, index_file = current_dir_prepare_index_kwargs()
        raman_index = initialize_index_from_source_files(
            files=source_files,
            index_file=index_file,
            force_reindex=True,
            persist_to_file=True,
        )
        if not raman_index.dataset:
            console.print(
                f"No Raman files could be indexed in {Path.cwd()}", style="bold red"
            )
            raise typer.Exit(code=1)

        kwargs["index"] = raman_index
        index_file = raman_index.index_file
        dump_default_config(LOCAL_CONFIG_FILE)

    if index_file is not None:
        index_file = Path(index_file).resolve()
        if not index_file.exists():
            console.print(
                f"Index file does not exist but is required. {index_file}",
                style="bold red",
            )
            raise typer.Exit(code=1)
        kwargs["index"] = index_file

    typer.echo(
        f"Starting raman_fitting with CLI. run mode: {run_mode} and kwargs: {kwargs}"
    )

    try:
        delegator = MainDelegator(**kwargs)
        results = delegator.run()
        console.print("Processing completed successfully!", style="bold green")
        return results
    except (ValueError, KeyError) as e:
        logger.error(f"Error during processing: {str(e)}")
        typer.echo("Could not run raman_fitting. Check the logs for more details.")
        raise typer.Exit(code=1)
    finally:
        logger.remove()
        from loguru import logger

        logger.disable("raman_fitting")


@run_app.command()
def current_dir(
    models: Annotated[
        list[str],
        typer.Option(
            default_factory=list, help="Selection of models to use for deconvolution."
        ),
    ],
    sample_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of SampleIDs from index to run over.",
        ),
    ],
    group_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of sample groups from index to run over.",
        ),
    ],
    fit_models: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of the Region that are to used for fitting.",
        ),
    ],
    index_file: Annotated[Optional[Path], typer.Option()] = None,
    log_file: Annotated[Optional[Path], typer.Option("--log-file")] = None,
    log_level: Annotated[str, typer.Option("--log-level")] = "INFO",
):
    """Run the application in the current directory mode."""
    run_command(
        models=models,
        sample_ids=sample_ids,
        group_ids=group_ids,
        fit_models=fit_models,
        run_mode=RunModes.CURRENT_DIR,
        index_file=index_file,
        log_file=log_file,
        log_level=log_level,
    )


@run_app.command()
def examples(
    log_file: Annotated[Optional[Path], typer.Option("--log-file")] = None,
    log_level: Annotated[str, typer.Option("--log-level")] = "DEBUG",
):
    """Run the application in examples mode."""
    run_command(
        run_mode=RunModes.EXAMPLES,
        log_file=log_file,
        log_level=log_level,
    )


@run_app.command()
def normal(
    models: Annotated[
        list[str],
        typer.Option(
            default_factory=list, help="Selection of models to use for deconvolution."
        ),
    ],
    sample_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of SampleIDs from index to run over.",
        ),
    ],
    group_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of sample groups from index to run over.",
        ),
    ],
    fit_models: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of the Region that are to used for fitting.",
        ),
    ],
    index_file: Annotated[Optional[Path], typer.Option()] = None,
    log_file: Annotated[Optional[Path], typer.Option("--log-file")] = None,
    log_level: Annotated[str, typer.Option("--log-level")] = "INFO",
):
    """Run the application in normal mode."""
    run_command(
        models=models,
        sample_ids=sample_ids,
        group_ids=group_ids,
        fit_models=fit_models,
        run_mode=RunModes.NORMAL,
        index_file=index_file,
        log_file=log_file,
        log_level=log_level,
    )


@run_app.command()
def pytest(
    models: Annotated[
        list[str],
        typer.Option(
            default_factory=list, help="Selection of models to use for deconvolution."
        ),
    ],
    sample_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of SampleIDs from index to run over.",
        ),
    ],
    group_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of sample groups from index to run over.",
        ),
    ],
    fit_models: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of the Region that are to used for fitting.",
        ),
    ],
    index_file: Annotated[Optional[Path], typer.Option()] = None,
    log_file: Annotated[Optional[Path], typer.Option("--log-file")] = None,
    log_level: Annotated[str, typer.Option("--log-level")] = "INFO",
):
    """Run the application in pytest mode."""
    run_command(
        models=models,
        sample_ids=sample_ids,
        group_ids=group_ids,
        fit_models=fit_models,
        run_mode=RunModes.PYTEST,
        index_file=index_file,
        log_file=log_file,
        log_level=log_level,
    )


@run_app.command()
def debug(
    models: Annotated[
        list[str],
        typer.Option(
            default_factory=list, help="Selection of models to use for deconvolution."
        ),
    ],
    sample_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of SampleIDs from index to run over.",
        ),
    ],
    group_ids: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of sample groups from index to run over.",
        ),
    ],
    fit_models: Annotated[
        list[str],
        typer.Option(
            default_factory=list,
            help="Selection of names of the Region that are to used for fitting.",
        ),
    ],
    index_file: Annotated[Optional[Path], typer.Option()] = None,
    log_file: Annotated[Optional[Path], typer.Option("--log-file")] = None,
    log_level: Annotated[str, typer.Option("--log-level")] = "INFO",
):
    """Run the application in debug mode."""
    run_command(
        models=models,
        sample_ids=sample_ids,
        group_ids=group_ids,
        fit_models=fit_models,
        run_mode=RunModes.DEBUG,
        index_file=index_file,
        log_file=log_file,
        log_level=log_level,
    )


if __name__ == "__main__":
    run_app()
