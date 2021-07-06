"""
Created on Sun Jun  6 09:35:02 2021

@author: DW
"""

import unittest
from functools import partial

import pytest
from lmfit import Model

import raman_fitting
from raman_fitting.deconvolution_models.base_model import _SUBSTRATE_PEAK, BaseModel

_SUBSTRATE_PREFIX = _SUBSTRATE_PEAK.split("peak")[0]


def _get_list_components(bm):
    _listcompsprefix = partial(map, lambda x,: getattr(x, "prefix"))
    _bm_prefix = list(_listcompsprefix(bm.lmfit_model.components))
    return _bm_prefix


class TestBaseModel(unittest.TestCase):
    def test_empty_base_model(self):
        bm = BaseModel()
        self.assertEqual(bm.model_name, "")
        self.assertFalse(bm.has_substrate)
        bm.add_substrate()
        self.assertIn(bm.model_name, _SUBSTRATE_PEAK)
        self.assertEqual(type(bm.lmfit_model).__qualname__, "GaussianModel")
        self.assertIn(bm.lmfit_model.prefix, _SUBSTRATE_PEAK)
        self.assertTrue(issubclass(type(bm.lmfit_model), Model))

    def test_base_model_2peaks(self):
        bm = BaseModel(model_name="K2+D+G")

        self.assertListEqual(_get_list_components(bm), ["D_", "G_"])
        bm.add_substrate()
        self.assertListEqual(_get_list_components(bm), ["D_", "G_", _SUBSTRATE_PREFIX])
        bm.remove_substrate()
        self.assertListEqual(_get_list_components(bm), ["D_", "G_"])

    def test_base_model_wrong_chars_model_name(self):
        bm = BaseModel(model_name="K2+---////+  +7 +K1111+1D+D2")
        self.assertListEqual(_get_list_components(bm), ["D2_"])
        bm.add_substrate()
        self.assertListEqual(_get_list_components(bm), ["D2_", _SUBSTRATE_PREFIX])


if __name__ == "__main__":
    unittest.main()
