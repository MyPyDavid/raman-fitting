#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple

import pandas as pd
import numpy as np

from .slicer import SpectraInfo
from .cleaner import SpectrumCleaner

 
class PrepareMean_Fit():
    '''
    Operations done in this class: read-raw-spectrum > savgol_filter > 
    normalization on (filtered,despiked,baseline-corrected) G peak
    for i in peak range:
        do baseline substraction
        take normalizion in normal window
    slice, filter, despike, slice, subtract baseline, '''
    
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
        
        
    #    spec_array_sliced = dict([(i[0],i[1][ind]) for i in array_test])
    
#    norm_spec._asdict()
        return pd.DataFrame( norm_spec._asdict()).set_index(list(spec_info.keys()))
    
    def calc_mean_from_spclst(speclst):
        spectras = pd.concat(speclst)
        mean_spclst = namedtuple('MeanSpectras' , 'windowname sID_rawcols sIDmean_col mean_info mean_spec')
        results_spclst = []
        for wn,wgrp in spectras.groupby('windowname'):
    #        pd.DataFrame(wgrp.index.names, wgrp.index.to_flat_index())
#            wgrp.plot(x='ramanshift',y='intensity',title=wn)
            mean_wn = pd.DataFrame()
            mean_info = wgrp.index.to_frame().drop_duplicates()
            mean_info = mean_info.set_index('FileStem')
            sID = mean_info.SampleID.unique()[0]
            sIDmean_col = f'int_{sID}_mean'
            
            for idx,idxgrp in wgrp.groupby(level='FileStem'):
    #            idxgrp.plot(x='ramanshift',y='intensity_raw',title=f'{wn} {idx}')
                pos_spectrum = idxgrp[['ramanshift','intensity']].rename(columns={'intensity' : f'intensity_{idx}'}).set_index('ramanshift')
                if mean_wn.empty:
                    mean_wn = pos_spectrum
                else:
    #                mean_wm.update(pos_spectrum)
#                    print(wn,idx)
                    mean_wn = pd.merge(mean_wn,pos_spectrum,on='ramanshift',how='left')
            sID_rawcols = [i for i in mean_wn.columns if 'intensity' in i]
            mean_spec = mean_wn.assign(**{sIDmean_col : mean_wn[sID_rawcols].mean(axis=1)})
            diff_mean_info = []
            for infFS,infFSgrp in mean_info.groupby(level='FileStem'):
                diff_mean_spec = mean_spec[sIDmean_col] - mean_spec[f'intensity_{infFS}']
                diff_mean_info.append(np.abs(diff_mean_spec).sum())
            mean_info = mean_info.assign(**{f'diff_from_{sIDmean_col}' : diff_mean_info})
            
            prep_fit_spec = mean_spclst(wn,sID_rawcols, sIDmean_col,mean_info, mean_spec)
            results_spclst.append(prep_fit_spec)
        return results_spclst