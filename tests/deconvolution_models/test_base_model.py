"""
Created on Sun Jun  6 09:35:02 2021

@author: DW
"""

from functools import partial

import unittest
import pytest

from lmfit import Model

import raman_fitting

from raman_fitting.deconvolution_models.base_model import BaseModel, _SUBSTRATE_PEAK


class TestBaseModel(unittest.TestCase):
    
    def test_empty_base_model(self):
        bm =BaseModel()
        assert bm.model_name == ''
        assert bm.has_substrate == False
        bm.add_substrate()
        assert bm.model_name in _SUBSTRATE_PEAK
        assert type(bm.lmfit_model).__qualname__ == 'GaussianModel'
        assert bm.lmfit_model.prefix in _SUBSTRATE_PEAK
        assert issubclass(type(bm.lmfit_model), Model)
        
    def test_base_model_2peaks(self):
        bm =BaseModel(model_name='K2+D+G')
        
        _listcompsprefix = partial(map, lambda x,: getattr(x, 'prefix'))
        _bm_prefix = list(_listcompsprefix(bm.lmfit_model.components))
        assert _bm_prefix == ['D', 'G']
        bm.add_substrate()
        _bm_prefix = list(_listcompsprefix(bm.lmfit_model.components))
        assert _bm_prefix == ['D', 'G', 'Si1']
        bm.remove_substrate()
        _bm_prefix = list(_listcompsprefix(bm.lmfit_model.components))
        assert _bm_prefix == ['D', 'G']

def _testing():
    bm =BaseModel(model_name='K2+---////+  +7 +K1111+1D+D2')
    bm
    bm.has_substrate
    bm.include_substrate = True
    bm.model_name
    bm.lmfit_model
    bm.add_substrate()
    bm
    bm.model_name
    bm.lmfit_model
    bm.remove_substrate()
    bm.model_name = 'K2+7+K1111+1D+D2'
    bm.include_substrate
    bm.lmfit_model
    bm.model_name = 'K2+7+K1111+1D+D2+Si1'
    bm.include_substrate
    bm.lmfit_model
    
    