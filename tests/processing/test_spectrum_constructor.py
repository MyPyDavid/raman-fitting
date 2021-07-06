# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:01:57 2021

@author: zmg
"""

import unittest
from pathlib import Path

import pytest

from raman_fitting.datafiles import example_files
from raman_fitting.processing.spectrum_constructor import (
    SpectrumDataCollection,
    SpectrumDataLoader,
)


class TestSpectrumDataLoader(unittest.TestCase):
    def setUp(self):
        _example_path = Path(example_files.__path__[0])
        _example_files_contents = list(Path(_example_path).rglob("*txt"))

        self.testfile = next(
            filter(lambda x: "testDW38C_pos4" in x.name, _example_files_contents)
        )

    def test_SpectrumDataLoader_empty(self):

        spd = SpectrumDataLoader()
        self.assertEqual(spd.file.name, "empty.txt")

    def test_SpectrumDataLoader_file(self):
        pass
        # spd = SpectrumDataLoader(self.testfile)

        # self = spcoll


# class SpectrumData():
def _testing():
    spectrum_data = SpectrumDataLoader(
        file=meannm[-1], run_kwargs=_spectrum_position_info_kwargs, ovv=meangrp
    )
    self = spectrum_data
    self._despike.Z_t
    self._despike.input_intensity
    self = self._despike
    rr = RL.export_collect[0]
    spec = rr.fitter.spectra_arg._spectra[0]


if __name__ == "__main__":
    self = TestSpectrumDataLoader()
