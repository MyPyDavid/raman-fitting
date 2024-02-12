# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:01:57 2021

@author: zmg
"""

import unittest
from pathlib import Path

from raman_fitting.config.settings import (
    InternalPathSettings,
    get_run_mode_paths,
    RunModes,
)
from raman_fitting.imports.spectrum.spectrum_constructor import (
    SpectrumDataLoader,
)

internal_paths = InternalPathSettings()


class TestSpectrumDataLoader(unittest.TestCase):
    def setUp(self):
        self.example_files = list(internal_paths.example_fixtures.rglob("*txt"))

    def test_SpectrumDataLoader_empty(self):
        spd = SpectrumDataLoader("empty.txt")
        self.assertEqual(spd.file, "empty.txt")
        self.assertEqual(spd.clean_spectrum, None)

    def test_SpectrumDataLoader_file(self):
        for file in self.example_files:
            spd = SpectrumDataLoader(
                file, run_kwargs=dict(SampleID=file.stem, SamplePos=1)
            )
            self.assertEqual(len(spd.clean_spectrum.spectrum), 1600)
            assert len(spd.clean_spectrum.spec_windows) >= 5


if __name__ == "__main__":
    unittest.main()
