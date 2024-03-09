#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from raman_fitting.config.path_settings import RunModes
from loguru import logger
from .utils import get_package_version


def main():
    """
    The command line interface for raman_fitting
    """

    parser = argparse.ArgumentParser(
        description="Command-line interface for raman_fitting package main."
    )

    parser.add_argument(
        "-M",
        "-m",
        "--run-mode",
        type=RunModes,
        # choices=,
        help="running mode of package, for testing",
        default="normal",
    )

    parser.add_argument(
        "-sIDs",
        "--sample_ids",
        nargs="+",
        default=[],
        help="Selection of names of SampleIDs from index to run over.",
    )

    parser.add_argument(
        "-sGrps",
        "--sample_groups",
        nargs="+",
        default=[],
        help="Selection of names of sample groups from index to run over.",
    )

    parser.add_argument(
        "--fit_model_specific_names",
        nargs="+",
        default=[],
        help="Selection of names of the composite LMfit models to use for fitting.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {}".format(get_package_version()),
        help="Prints out the current version of the raman_fitting distribution, via importlib.metadata.version",
    )

    # Execute the parse_args() method
    args = parser.parse_args()

    # import the raman_fitting package
    import raman_fitting as rf

    extra_kwargs = {}
    if args.run_mode == RunModes.EXAMPLES:
        extra_kwargs.update(
            {"fit_model_specific_names": ["2peaks", "3peaks", "4peaks"]}
        )
    logger.info(f"Starting raman_fitting with CLI args:\n{args}")
    kwargs = {**vars(args), **extra_kwargs}
    _main_run = rf.MainDelegator(**kwargs)
