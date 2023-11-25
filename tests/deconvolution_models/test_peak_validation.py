# flake8: noqa

import unittest

import pytest
from lmfit import Model

import raman_fitting
from raman_fitting.deconvolution_models.peak_validation import (
    NotFoundAnyModelsWarning,
    PeakModelValidator,
)


class TestPeakModelValidator(unittest.TestCase):
    def setUp(self):
        self.pmv = PeakModelValidator()

    @unittest.skip("validation is built in to the model")
    def test_validation_inspect_models(self):
        _valid = self.pmv.validation_inspect_models([str])
        self.assertTrue(_valid)
        self.assertFalse(_valid[1][0].valid)
        self.assertIn("has no attr", _valid[1][0].message)

        _valid = self.pmv.validation_inspect_models([Model])
        self.assertTrue(_valid)
        self.assertFalse(_valid[1][0].valid)
        self.assertIn("Unable to initialize model", _valid[1][0].message)

    @unittest.skip("not yet implemented")
    def test_get_cmap_list(self):
        _cmap = self.pmv.get_cmap_list([], cmap_options=())
        self.assertEqual(_cmap, [])
        _cmap = self.pmv.get_cmap_list(
            [1] * 50, cmap_options=(), fallback_color=self.pmv.fallback_color
        )
        self.assertEqual(_cmap, [self.pmv.fallback_color] * 50)
        _cmap = self.pmv.get_cmap_list([1] * 5)
        self.assertEqual(len(_cmap), 5)


if __name__ == "__main__":
    unittest.main()
