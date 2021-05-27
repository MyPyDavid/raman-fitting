# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple

import pandas as pd
import numpy as np

# from raman_fitting.processing.slicer import SpectraInfo
# from raman_fitting.processing.cleaner import SpectrumCleaner

class SpectrumPreparator():

    def __init__(self):
        pass

class PrepareMean_Fit():
    '''
    Operations done in this class: read-raw-spectrum > savgol_filter > 
    normalization on (filtered,despiked,baseline-corrected) G peak
    for i in peak range:
        do baseline substraction
        take normalizion in normal window
    slice, filter, despike, slice, subtract baseline.
    '''

    def __init__(self):
        pass

    def subtract_baseline(sample_spectra):
        speclst = []
        for spec_raw in sample_spectra:
    #        spectrum = namedtuple('Spectrum', 'ramanshift intensity')
            FirstOrder_spec = SpectrumCleaner(SpectraInfo.spec_slice(spec_raw,'1st_order'))
    #        SpectrumCleaner(SpectraInfo.spec_slice(norm_spec,windowname)).spec
            norm_spec = SpectrumCleaner.normalization(FirstOrder_spec,spec_raw)
            # TODO appending each region and make columns of position and mean for fitting and plotting....
    #        cleaner = SpectrumCleaner(SpecWindow)
            for windowname,(low,high) in SpectraInfo.SpectrumWindows().items():
                window_spec = SpectraInfo.spec_slice(norm_spec,windowname)
                cleaned_window_spec = SpectrumCleaner(window_spec)
    #            cleaned_wind_spec.plot()
                speclst.append(PrepareMean_Fit.norm_spec_unpack_appender(cleaned_window_spec.cleaned_spec))    
        return speclst

    def norm_spec_unpack_appender(norm_spec):
        spec_length = norm_spec.spectrum_length
        array_test = [(n,i) for n,i in zip(norm_spec._fields,norm_spec) if 'array' in str(type(i))]
        array_cols = [i[0] for i in array_test] # arrays = [i[1] for i in array_test]
        spec_info = dict([(i,getattr(norm_spec,i)) for i in norm_spec._fields if i not in array_cols])
#      spec_array_sliced = dict([(i[0],i[1][ind]) for i in array_test])
#      norm_spec._asdict()
        return pd.DataFrame( norm_spec._asdict()).set_index(list(spec_info.keys()))
