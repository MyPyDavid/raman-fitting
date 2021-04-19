#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import namedtuple


import numpy as np
import pandas as pd

from scipy import signal
from scipy.stats import linregress


from .slicer import SpectraInfo
from .spectrum_template import Spectrum


class SpectrumCleaner():
    ''' Takes a Spectrum and cleans the data.
        Input:  
    
    '''
    
    def __init__(self,spec):
#        self.raw_intensity = spec.intensity
        self.spec = spec
#        self.int_savgol = SpectrumCleaner.filtered(spec.intensity)
        self.Despike_raw = Despike(spec.intensity_raw)
        self.despiked_raw_intensity = self.Despike_raw.despiked_int
        self.despiked_raw_df = self.Despike_raw.df
        self.blcorr_desp_intensity_raw,self.blc_dsp_int_raw_lin = SpectrumCleaner.subtract_baseline(self,  self.despiked_raw_intensity)
        
        self.Despike_filter = Despike(spec.intensity)
        self.despiked_intensity = self.Despike_filter.despiked_int
#        breakpoint()
        self.despiked_df = self.Despike_filter.df
        self.blcorr_desp_intensity,self.blc_dsp_int_linear = SpectrumCleaner.subtract_baseline(self,  self.despiked_intensity)
        
#TODO self.df = SpectrumCleaner.pack_to_dataframe(self)
        self.cleaned_spec = SpectrumCleaner.cleaned_out_spec(self)
        
    def filtered(intensity):
#        fltrd_spec = self.raw_spec
        int_savgol_fltr = signal.savgol_filter(intensity, 13, 3, mode='nearest')
#        fltrd_spec._replace(intensity=int_savgol_fltr)
        return int_savgol_fltr
    
    def pack_to_df_names():
         return ('ramanshift', 'intensity_raw', 'intensity','int_raw_despike',
                 'int_filter_despike', 'int_filter_despike_blcorr', 'int_raw_despike_blcorr')
         
    def pack_to_dataframe(self):
        cols = [self.spec.ramanshift, self.spec.intensity_raw,  self.spec.intensity, 
                self.despiked_raw_intensity, self.despiked_intensity, self.blcorr_desp_intensity, self.blcorr_desp_intensity_raw] 
        names = SpectrumCleaner.pack_to_df_names()
        return pd.DataFrame(dict(zip(names,cols)))
    
    def cleaned_out_spec(self):
        cleanSpec_template = self.spec
        cleanSpec = cleanSpec_template._replace(intensity = self.blcorr_desp_intensity, intensity_raw = self.blcorr_desp_intensity_raw)
        return cleanSpec
    
    def plot(self):
        self.df.plot(x='ramanshift',y=[i for i in list(SpectrumCleaner.pack_to_df_names()[1:]) if 'blcorr' in i])     
        
    def subtract_baseline(self, i_fltrd_dspkd_input):
        rs = self.spec.ramanshift
        windowname = self.spec.windowname
#        self.spec = SpectraInfo.spec_slice(spec_raw,'1st_order')
#        i_fltrd_dspkd_input = Despike(self.spec.intensity).despiked_int
#        rs_min, rs_max = rs.min(), rs.max()
        
        if windowname == 'full':
            indx = SpectraInfo.ramanshift_slice_indx(rs, '1st_order')
            i_fltrd_dspkd_fit = i_fltrd_dspkd_input[indx]
        else:
            i_fltrd_dspkd_fit = i_fltrd_dspkd_input
        
        if windowname in ['1st_order','full', 'full_1st_2nd']:
            bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:20]),np.mean(i_fltrd_dspkd_fit[-20::])])
        elif windowname == '2nd_order':
            bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:5]),np.mean(i_fltrd_dspkd_fit[-5::])])
        else:
            bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:10]),np.mean(i_fltrd_dspkd_fit[-10::])])
        i_blcor = i_fltrd_dspkd_input - (bl_linear[0]*rs+bl_linear[1])
#        blcor = pd.DataFrame({'Raman-shift' : w, 'I_bl_corrected' :i_blcor, 'I_raw_data' : i})
        return i_blcor,bl_linear
    
    def normalization(FirstOrder_spec,output_spec,method='simple'):
        if 'simple' in method:
            indx_norm = SpectraInfo.ramanshift_slice_indx(FirstOrder_spec.spec.ramanshift,'normalization')
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(spec,'normalization'))
            normalization_intensity  = FirstOrder_spec.blcorr_desp_intensity[indx_norm].max()
            
        elif 'fit' in method:
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(FirstOrder_spec,'1st_order'))
            normalization = NormalizeFit(FirstOrder_spec,plotprint = False)
            normalization_intensity = normalization['IG']
            
        norm_dict = {'norm_factor' : 1/normalization_intensity, 'norm_method' : method}
        int_fields = [i for i in output_spec._fields if 'intensity' in i]
        extra_info_flds = [i for i in output_spec._fields if i not in int_fields]
        [norm_dict.update({i : getattr(output_spec,i)}) for i in extra_info_flds]
        [norm_dict.update({i : getattr(output_spec, i)/normalization_intensity}) for i in int_fields]
        norm_info = namedtuple('norm_info','norm_factor norm_method')
        NormSpec = namedtuple('spectrum_normalized', Spectrum().template._fields + norm_info._fields)(**norm_dict)
        return NormSpec
    
    

#
class Despike():
    ''' Despiking algorith from reference literature:
    Let Y1;...;Yn represent the values of a single Raman spectrum recorded at equally spaced wavenumbers.
    From this series, form the detrended differenced seriesr Yt ...:This simple
    ata processing step has the effect of annihilating linear and slow movingcurve linear trends, however,
    sharp localised spikes will be preserved.Denote the median and the median absolute deviation of 
    D.A. Whitaker, K. Hayes. Chemometrics and Intelligent Laboratory Systems 179 (2018) 82–84
    https://doi.org/10.1016/j.chemolab.2018.06.009'''
    def __init__(self,input_intensity):
        self.intensity = SpectraInfo.check_input_return_intensity(input_intensity)
        self.Zt = Despike.calc_Z(self.intensity)
        self.Zt_filter = Despike.Z_filter(self.Zt)
        self.despiked_int = Despike.fixer(self.intensity, self.Zt_filter)
        self.df = Despike.pack_to_df(self)
        self.dict = Despike.pack_to_dict(self)
#        self. = Despike.fixer(intensity,Despike.Z_filter(intensity))
    
    def pack_to_df(self):
        cols =  [self.intensity, self.Zt, self.Zt_filter, self.despiked_int] 
        names = ['intensity','Zt', 'Zt_threshold','int_despike']
        return pd.DataFrame(dict(zip(names,cols)))
    
    def pack_to_dict(self):
        cols =  [self.intensity, self.Zt, self.Zt_filter, self.despiked_int] 
        names = ['intensity','Zt', 'Zt_threshold','int_despike']
        return dict(zip(names,cols))
    
    def plot_Z(self):
        self.df.plot(y=['Zt', 'Zt_threshold'],alpha=0.5)
   # TODO still finish...
    def calc_Z(intensity): 
#        y = intensity[Ystr]
        dYt = np.append(np.diff(intensity),0)
        #    dYt = intensity.diff()
        dYt_Median = np.median(dYt)
        #    M = dYt.median()
        #    dYt_M =  dYt-M
        dYt_MAD = np.median(abs(dYt - dYt_Median))
        #    MAD = np.mad(dYt)
        Z_t = (0.6745*(dYt-dYt_Median)) / dYt_MAD
        #    intensity = blcor.assign(**{'abs_Z_t': Z_t.abs()})
        return Z_t
    
    def Z_filter(Z_t, Z_threshold = 6):
        Z_t_filtered = Z_t
        Z_t_filtered[np.abs(Z_t) > Z_threshold] = np.nan
        Z_t_filtered[0] = Z_t_filtered[-1] = np.nan
        return Z_t_filtered
#        Z_threshold = 3.5
#        Z_t_filtered = [Z_t
#        Z_t_filtered[Z_filter_indx] = np.nan
#        y_out,n = intensity,len(intensity)
    
    def fixer(intensity,Z_t_filtered,ma=10):
        n = len(intensity)
        i_despiked = intensity
        spikes = np.where(np.isnan(Z_t_filtered))
        for i in list(spikes[0]):
            w = np.arange(max(1,i-ma),min(n,i+ma))
            w = w[~np.isnan(Z_t_filtered[w])]
            i_despiked[i] = np.mean(intensity[w]) 
        return i_despiked