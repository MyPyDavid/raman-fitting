# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:12:56 2021

@author: zmg
"""

import unittest

import pandas as pd
import pytest
from lmfit import Model

import raman_fitting
from raman_fitting.deconvolution_models.fit_models import Fitter, PrepareParams

# try:
#     import raman_fitting


# except Exception as e:
#     print(f'pytest file {__file__}, {__name__} error {e}')


class TestFitter(unittest.TestCase):
    def test_empty_Fitter(self):
        ft = Fitter({})
        self.assertFalse(ft.start_fit)
        self.assertEqual(ft.spectra, {})
        ft.fit_delegator()


class TestPrepareParams(unittest.TestCase):
    def test_empty_PrepareParams(self):
        # pp =
        with self.assertRaises(AttributeError):
            PrepareParams({})


def _testing():

    self = ft
    self = prep


if __name__ == "__main__":
    unittest.main()
