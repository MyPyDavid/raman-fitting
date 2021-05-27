# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple

import pandas as pd
import numpy as np

# from raman_fitting.processing.slicer import SpectraInfo
# from raman_fitting.processing.cleaner import SpectrumCleaner

def _testing():
    spec_raw = sample_spectra[1]
    spec = spec_raw
    windowname = '1st_order'
    
    spec = norm_spec

