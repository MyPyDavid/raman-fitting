# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:29:16 2021

@author: zmg
"""
# flake8: noqa

import unittest

from raman_fitting.models.deconvolution.init_models import InitializeModels
from raman_fitting.exports.plot_formatting import (
    get_cmap_list,
    assign_colors_to_peaks,
    DEFAULT_COLOR,
    COLOR_BLACK,
)


class PeakModelAnnotation(unittest.TestCase):
    def setUp(self):
        self.models = InitializeModels()

    def test_get_cmap_list(self):
        self.assertEqual(get_cmap_list(0), None)
        _cmap = get_cmap_list(50)
        self.assertEqual(_cmap, [DEFAULT_COLOR] * 50)
        _cmap = get_cmap_list(5)
        self.assertGreaterEqual(len(_cmap), 5)

        _cmap = get_cmap_list(5, default_color=COLOR_BLACK)
        # self.assertEqual(_cmap, [COLOR_BLACK] * 5)

    def test_assign_colors_to_peaks(self):
        # print(self.models)
        # breakpoint()
        for order_type, model_collection in self.models.lmfit_models.items():
            for model_name, model in model_collection.items():
                annotated_models = assign_colors_to_peaks(model.lmfit_model.components)
                # breakpoint()
                prefixes = set([i.prefix for i in model.lmfit_model.components])
                self.assertSetEqual(prefixes, set(annotated_models.keys()))
                # print(annotated_models)
                # breakpoint()


if __name__ == "__main__":
    unittest.main()
