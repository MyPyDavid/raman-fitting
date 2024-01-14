# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:29:16 2021

@author: zmg
"""
# flake8: noqa

import unittest

import pytest
from lmfit import Model

from raman_fitting.models.deconvolution.init_models import InitializeModels
from raman_fitting.exports.plot_formatting import (
    get_cmap_list,
    assign_colors_to_peaks,
    DEFAULT_COLOR,
    COLOR_BLACK,
)


def _testing():
    peak1, res1_peak_spec, res2_peak_spec = (
        modname_1,
        fitres_1,
        fitres_2,
    )
    peak1, res1_peak_spec = "1st_6peaks+Si", self._1st["1st_6peaks+Si"]


class PeakModelAnnotation(unittest.TestCase):
    def setUp(self):
        self.models = InitializeModels()

    @unittest.skip("not yet implemented")
    def test_get_cmap_list(self):
        self.assertEqual(get_cmap_list(0), None)
        _cmap = get_cmap_list([1] * 50)
        self.assertEqual(_cmap, [DEFAULT_COLOR] * 50)
        _cmap = get_cmap_list([1] * 5)
        self.assertEqual(len(_cmap), 5)

        _cmap = get_cmap_list([1] * 5, default_color=COLOR_BLACK)
        self.assertEqual(_cmap, [COLOR_BLACK] * 5)

    @unittest.skip("not yet implemented")
    def test_assign_colors_to_peaks(self):
        annotated_models = assign_colors_to_peaks(models)


if __name__ == "__main__":
    unittest.main()
