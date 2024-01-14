"""
Created on Sun Jun  6 09:35:02 2021

@author: DW
"""

import unittest
from functools import partial

from pydantic import ValidationError

from raman_fitting.models.deconvolution.base_model import (
    SUBSTRATE_PEAK,
    BaseLMFitModel,
)

SUBSTRATE_PREFIX = SUBSTRATE_PEAK.split("peak")[0]


def helper_get_list_components(bm):
    _listcompsprefix = partial(map, lambda x,: getattr(x, "prefix"))
    _bm_prefix = list(_listcompsprefix(bm.lmfit_model.components))
    return _bm_prefix


class TestBaseLMFitModel(unittest.TestCase):
    def test_empty_base_model(self):
        self.assertRaises(ValidationError, BaseLMFitModel)
        self.assertRaises(ValidationError, BaseLMFitModel, name="Test_empty")
        self.assertRaises(
            ValidationError,
            BaseLMFitModel,
            peaks="A+B",
        )
        self.assertRaises(
            ValidationError,
            BaseLMFitModel,
            name="Test_empty",
            peaks="A+B",
            window_name="full",
        )

    def test_base_model_2peaks(self):
        bm = BaseLMFitModel(name="Test_2peaks", peaks="K2+D+G", window_name="full")
        self.assertSetEqual(set(helper_get_list_components(bm)), set(["D_", "G_"]))
        bm.add_substrate()
        self.assertSetEqual(
            set(helper_get_list_components(bm)), set(["D_", "G_", SUBSTRATE_PREFIX])
        )
        bm.remove_substrate()
        self.assertSetEqual(set(helper_get_list_components(bm)), set(["D_", "G_"]))

    def test_base_model_wrong_chars_model_name(self):
        bm = BaseLMFitModel(
            name="Test_wrong_chars",
            peaks="K2+---////+  +7 +K1111+1D+D2",
            window_name="full",
        )
        self.assertSetEqual(set(helper_get_list_components(bm)), set(["D2_"]))
        bm.add_substrate()
        self.assertSetEqual(
            set(helper_get_list_components(bm)), set(["D2_", SUBSTRATE_PREFIX])
        )
