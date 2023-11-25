"""
Created on Sun Jun  6 09:35:02 2021

@author: DW
"""

import unittest
from functools import partial
from operator import itemgetter

import pytest
from lmfit import Model

from raman_fitting.deconvolution_models.base_model import (
    SUBSTRATE_PEAK,
    BaseModelCollection,
)
from pydantic import ValidationError

SUBSTRATE_PREFIX = SUBSTRATE_PEAK.split("peak")[0]


def helper_get_list_components(bm):
    _listcompsprefix = partial(map, lambda x,: getattr(x, "prefix"))
    _bm_prefix = list(_listcompsprefix(bm.lmfit_model.components))
    return _bm_prefix


class TestBaseModel(unittest.TestCase):
    def test_empty_base_model(self):
        self.assertRaises(ValidationError, BaseModelCollection)
        self.assertRaises(ValidationError, BaseModelCollection, name="Test_empty")
        self.assertRaises(ValidationError, BaseModelCollection, peaks="A+B")
        bm = BaseModelCollection(name="Test_empty", peaks="A+B")

    def test_base_model_2peaks(self):
        bm = BaseModelCollection(name="Test_2peaks", peaks="K2+D+G")
        print(bm)

        self.assertSetEqual(set(helper_get_list_components(bm)), set(["D_", "G_"]))
        bm.add_substrate()
        self.assertSetEqual(
            set(helper_get_list_components(bm)), set(["D_", "G_", SUBSTRATE_PREFIX])
        )
        bm.remove_substrate()
        self.assertSetEqual(set(helper_get_list_components(bm)), set(["D_", "G_"]))

    def test_base_model_wrong_chars_model_name(self):
        bm = BaseModelCollection(
            name="Test_wrong_chars", peaks="K2+---////+  +7 +K1111+1D+D2"
        )
        self.assertSetEqual(set(helper_get_list_components(bm)), set(["D2_"]))
        bm.add_substrate()
        self.assertSetEqual(
            set(helper_get_list_components(bm)), set(["D2_", SUBSTRATE_PREFIX])
        )
