#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Optional
from typing_extensions import Annotated


from enum import StrEnum, auto
from loguru import logger
from raman_fitting.config.path_settings import RunModes
from raman_fitting.delegating.main_delegator import MainDelegator
from .utils import get_package_version

import typer


class MakeTypes(StrEnum):
    INDEX = auto()
    CONFIG = auto()


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
):
    kwargs = {"run_mode": run_mode}
    if run_mode == RunModes.NORMAL:
        pass
        # _org_index = OrganizeRamanFiles()
        # RL = RamanLoop(_org_index, run_mode ='normal')
    elif run_mode.lower() == RunModes.DEBUG:
        pass
        # IDEA Add a FAST TRACK for DEBUG
    elif run_mode == RunModes.EXAMPLES:
        kwargs.update({"fit_model_specific_names": ["2peaks", "3peaks", "4peaks"]})
    logger.info(f"Starting raman_fitting with CLI args:\n{run_mode}")
    _main_run = MainDelegator(**kwargs)


@app.command()
def make(make_type: Annotated[MakeTypes, typer.Argument()]):
    if make_type == MakeTypes.INDEX:
        pass  # make index

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
