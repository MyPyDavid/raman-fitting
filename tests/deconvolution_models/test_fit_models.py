# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:12:56 2021

@author: zmg
"""

import pytest

try:
    import raman_fitting

    from raman_fitting.deconvolution_models.fit_models import Fitter
except Exception as e:
    print(f'pytest file {__file__}, {__name__} error {e}')



def _testing():
    ft = Fitter(spectra_collection)
    ft.fit_delegator()
    self = ft
    
    self = prep