# flake8: noqa

import unittest
import pytest

import raman_fitting
from raman_fitting.deconvolution_models.model_validation import PeakModelValidator

from lmfit import Model





class TestPeakModelValidator(unittest.TestCase):
    
    def _testing():
        peaks = PeakModelValidator()
        
        assert peaks.lmfit_models
        
        all([isinstance(i.peak_model, Model) for i in peaks.lmfit_models])
        all([isinstance(i.peak_model, Model) for i in peaks.get_dict().values()])
        
