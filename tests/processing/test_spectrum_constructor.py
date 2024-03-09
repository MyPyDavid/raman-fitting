# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:01:57 2021

@author: zmg
"""

import unittest

from raman_fitting.imports.spectrum.spectrum_constructor import (
    SpectrumDataLoader,
)

# class TestSpectrumDataLoader(unittest.TestCase):

def test_SpectrumDataLoader_empty():
    spd = SpectrumDataLoader("empty.txt")
    assert spd.file == "empty.txt"
    assert spd.clean_spectrum == None

def test_SpectrumDataLoader_file(example_files):
    for file in example_files:
        spd = SpectrumDataLoader(
            file, run_kwargs=dict(SampleID=file.stem, SamplePos=1)
        )
        assert len(spd.clean_spectrum.spectrum) == 1600
        assert len(spd.clean_spectrum.spec_regions) >= 5


if __name__ == "__main__":
    unittest.main()
