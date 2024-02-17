#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from raman_fitting.config.settings import RunModes
from loguru import logger


_RUN_MODES = ["normal", "testing", "debug", "make_index", "make_examples"]


try:
    import importlib.metadata

    _version = importlib.metadata.version("raman_fitting")
except ImportError:
    _version = "version.not.found"

_version_text = f"\n=== CLI raman_fitting version: {_version} ===\n"


def main():
    """
    The command line interface for raman_fitting
    """

    parser = argparse.ArgumentParser(
        description="Command-line interface for raman_fitting package main."
    )

    parser.add_argument(
        "-M",
        "--run-mode",
        type=RunModes,
        # choices=,
        help="running mode of package, for testing",
        default="normal",
    )

    parser.add_argument(
        "-sIDs",
        "--sample_IDs",
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
        # action=print(_version_text),
        action="version",
        version="%(prog)s {}".format(_version),
        # const=_version_text,
        help="Prints out the current version of the raman_fitting distribution, via importlib.metadata.version",
    )

    # Execute the parse_args() method
    args = parser.parse_args()

    # import the raman_fitting package
    import raman_fitting as rf

    extra_kwargs = {}
    if args.run_mode == "normal":
        pass
        # _org_index = OrganizeRamanFiles()
        # RL = RamanLoop(_org_index, run_mode ='normal')
    elif args.run_mode.lower() == "debug":
        pass
        # IDEA Add a FAST TRACK for DEBUG
    elif args.run_mode == "testing":
        pass
    elif args.run_mode == RunModes.MAKE_EXAMPLES:
        extra_kwargs.update(
            {"fit_model_specific_names": ["2peaks", "3peaks", "4peaks"]}
        )
    logger.info(f"Starting raman_fitting with CLI args:\n{args}")
    kwargs = {**vars(args), **extra_kwargs}
    _main_run = rf.MainDelegator(**kwargs)
