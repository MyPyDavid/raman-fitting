#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
import importlib.metadata


# def _testing():
#     args = parser.parse_args(['-M', 'debug'])
RUN_MODES = ["normal", "testing", "debug", "make_index", "make_examples"]

try:
    _version = importlib.metadata.version("raman_fitting")
except Exception as e:
    _version = "version.not.found"

_version_text = f"\n=== CLI raman_fitting version: {_version} ===\n"
# print(_version_text)


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
        type=str,
        choices=RUN_MODES,
        help="running mode of package, for testing",
        default="normal",
    )

    parser.add_argument(
        "-sIDs",
        "--sampleIDs",
        nargs="+",
        default=[],
        help="Selection of names of SampleIDs from index to run over.",
    )

    parser.add_argument(
        "-sGrps",
        "--samplegroups",
        nargs="+",
        default=[],
        help="Selection of names of sample groups from index to run over.",
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

    print(f"CLI args: {args}")
    if args.run_mode == "normal":
        pass
        # _org_index = OrganizeRamanFiles()
        # RL = RamanLoop(_org_index, run_mode ='normal')
    elif args.run_mode.upper() == "DEBUG":
        args.run_mode = args.run_mode.upper()
        # IDEA Add a FAST TRACK for DEBUG
    elif args.run_mode == "testing":
        pass

    _main_run = rf.MainDelegator(**vars(args))

    # return parser
