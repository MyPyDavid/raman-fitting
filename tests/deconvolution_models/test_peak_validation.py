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

    def test_pmv_valid_models(self):
        self.assertTrue(self.pmv.valid_models)

    def test_pmv_set_debug(self):
        self.assertFalse(self.pmv.debug)
        self.assertTrue(self.pmv._set_debug(**{"debug": True}))

    def test_get_subclasses_from_base(self):
        with self.assertWarns(NotFoundAnyModelsWarning):
            self.pmv.get_subclasses_from_base("")

        with self.assertWarns(NotFoundAnyModelsWarning):
            self.pmv.get_subclasses_from_base(str)

    def test_validation_inspect_models(self):

        _valid = self.pmv.validation_inspect_models([str])
        self.assertTrue(_valid)
        self.assertFalse(_valid[1][0].valid)
        self.assertIn("has no attr", _valid[1][0].message)

        _valid = self.pmv.validation_inspect_models([Model])
        self.assertTrue(_valid)
        self.assertFalse(_valid[1][0].valid)
        self.assertIn("Unable to initialize model", _valid[1][0].message)

    def test_get_cmap_list(self):

        _cmap = self.pmv.get_cmap_list([], cmap_options=())
        self.assertEqual(_cmap, [])
        _cmap = self.pmv.get_cmap_list(
            [1] * 50, cmap_options=(), fallback_color=self.pmv.fallback_color
        )
        self.assertEqual(_cmap, [self.pmv.fallback_color] * 50)
        _cmap = self.pmv.get_cmap_list([1] * 5)
        self.assertEqual(len(_cmap), 5)

    def test___getattr__(self):

        with self.assertRaises(AttributeError):
            self.pmv.fake_attr

    def test___iter__(self):
        _iter = [i for i in self.pmv]
        self.assertIsInstance(_iter, list)

    def test_if_lmfit_models(self):

        if self.pmv.lmfit_models:
            _getdict = self.pmv.get_dict()
            self.assertIsInstance(_getdict, dict)

            _getdict = self.pmv.get_model_dict(self.pmv.lmfit_models)
            self.assertIsInstance(_getdict, dict)


def _debugging():

    self = TestPeakModelValidator()
    peaks = PeakModelValidator()
    self.pmv = peaks
    # all([isinstance(i.peak_model, Model) for i in peaks.lmfit_models])
    # all([isinstance(i.peak_model, Model) for i in peaks.get_dict().values()])


if __name__ == "__main__":
    unittest.main()
