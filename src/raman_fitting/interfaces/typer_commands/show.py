from operator import attrgetter
from typing_extensions import Annotated
from pathlib import Path
from itertools import groupby

from raman_fitting.config import settings

from raman_fitting.config.path_settings import RunModes, INDEX_FILE_NAME
from raman_fitting.imports.files.file_finder import FileFinder
from raman_fitting.imports.files.index.factory import initialize_index_from_source_files
from raman_fitting.imports.spectrum.datafile_parsers import SPECTRUM_FILETYPE_PARSERS

import typer


LOCAL_INDEX_FILE = Path.cwd().joinpath(INDEX_FILE_NAME)
LOCAL_CONFIG_FILE = Path.cwd().joinpath("raman_fitting.toml")



show_app = typer.Typer()

@show_app.command()
def files(run_mode: Annotated[RunModes, typer.Option()] = RunModes.CURRENT_DIR):
    """Show the list of samples."""
    if run_mode == RunModes.CURRENT_DIR:
        file_finder = FileFinder(
            directory=Path.cwd(),
            suffixes=list(SPECTRUM_FILETYPE_PARSERS.keys()),
            exclusions=["."],
        )
        typer.echo(f"Found {len(file_finder.files)} files with: {file_finder}")
        for n, file in enumerate(file_finder.files):
            typer.echo(f"{n}: {file}")
    elif run_mode == RunModes.EXAMPLES:
        typer.echo("Running in examples mode. No files to show.")

@show_app.command()
def samples(run_mode: Annotated[RunModes, typer.Option()] = RunModes.CURRENT_DIR):
    """Show the list of samples."""
    if run_mode == RunModes.CURRENT_DIR:
        file_finder = FileFinder(
            directory=Path.cwd(),
            suffixes=list(SPECTRUM_FILETYPE_PARSERS.keys()),
            exclusions=["."],
        )
        raman_index = initialize_index_from_source_files(
            files=file_finder.files,
            force_reindex=True,
            persist_to_file=True,
        )
        # Sort the samples by group
        # Group the sorted samples by group
        grouped_samples = groupby(
            sorted(
                map(
                    attrgetter('sample'),
                    raman_index.raman_files
                )
            ),
            key=attrgetter("group")
        )

        # Print the grouped samples
        for group, items in grouped_samples:
            typer.echo(f"Group: {group}")
            ids = set(map(attrgetter('id'), items))
            typer.echo(f"Samples({len(ids)}): {', '.join(ids)}")
            typer.echo('---')
    elif run_mode == RunModes.EXAMPLES:
        typer.echo("Running in examples mode. No samples to show.")


@show_app.command()
def models(run_mode: Annotated[RunModes, typer.Option()] = RunModes.CURRENT_DIR):
    """Show the list of models."""
    if run_mode == RunModes.CURRENT_DIR:
        selected_models = settings.default_models

        # Determine the maximum widths for alignment
        max_region_width = max(
            len(region_name) for region_name in selected_models.keys()
        )
        max_model_width = max(
            len(model_name)
            for region_models in selected_models.values()
            for model_name in region_models.keys()
        )

        for region_name, region_models in selected_models.items():
            typer.echo(f"Region: {region_name.ljust(max_region_width)}")
            for model_name, model in region_models.items():
                msg = f"\t{model_name.ljust(max_model_width)}: {model.peaks}"
                if model.has_substrate:
                    msg += " (with substrate)"
                typer.echo(msg)
            typer.echo("---")
    elif run_mode == RunModes.EXAMPLES:
        typer.echo("Running in examples mode. No models to show.")
