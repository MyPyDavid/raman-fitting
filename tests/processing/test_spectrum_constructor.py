# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:01:57 2021

@author: zmg
"""

import unittest
from pathlib import Path

from raman_fitting.example_fixtures import example_files
from raman_fitting.imports.spectrum.spectrum_constructor import (
    SpectrumDataLoader,
)


class TestSpectrumDataLoader(unittest.TestCase):
    def setUp(self):
        self.files = list(example_files)
        # breakpoint()
        # self.testfile = next(
        #     filter(lambda x: "testDW38C_pos4" in x.name, files)
        # )

    def test_SpectrumDataLoader_empty(self):
        spd = SpectrumDataLoader("empty.txt")
        self.assertEqual(spd.file, "empty.txt")
        self.assertEqual(spd.clean_spectrum, None)

    def test_SpectrumDataLoader_file(self):
        for file in self.files:
            spd = SpectrumDataLoader(
                file, run_kwargs=dict(SampleID=file.stem, SamplePos=1)
            )
            self.assertEqual(len(spd.clean_spectrum.spectrum), 1600)
            assert len(spd.clean_spectrum.spec_windows) >= 5


if __name__ == "__main__":
    unittest.main()
