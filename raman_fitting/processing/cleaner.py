#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy

from collections import namedtuple


import numpy as np
import pandas as pd

from scipy import signal
from scipy.stats import linregress


# from raman_fitting.processing.slicer import SpectraInfo
from raman_fitting.processing.spectrum_template import SpectrumWindows, SpecTemplate, SpectrumWindowLimits

# from .slicer import SpectraInfo

# from .spectrum_constructor import SpectrumWindows, SpectrumDataLoader

class old_SpectrumCleaner():
    ''' Takes a Spectrum and cleans the data.
        Input:  
    
    '''
    
    def __init__(self,spec):
#        self.raw_intensity = spec.intensity
        self.spec = spec
#        self.int_savgol = SpectrumCleaner.filtered(spec.intensity)
        # self.Despike_raw = Despike(spec.intensityw)
        # self.despiked_raw_intensity = self.Despike_raw.despiked_int
        # self.despiked_raw_df = self.Despike_raw.df
        # self.blcorr_desp_intensity_raw,self.blc_dsp_int_raw_lin = SpectrumCleaner.subtract_baseline(self,  self.despiked_raw_intensity)
#        breakpoint()
        # self.despiked_df = self.Despike_filter.df
        self.blcorr_desp_intensity,self.blc_dsp_int_linear = SpectrumCleaner.subtract_baseline(self,  self.despiked_intensity)
        
        self.df = SpectrumCleaner.pack_to_dataframe(self)
        self.cleaned_spec = SpectrumCleaner.cleaned_out_spec(self)
        
    
        
    def apply_despike(self):
        self.despiked = Despike(self.spec.intensity)
        self.despiked_intensity = self.despiked.despiked_intensity
    
    
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
        self.df.plot(x='ramanshift',y=[i for i in list(self.pack_to_df_names()[1:]) if 'blcorr' in i])     
        
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
    
    def normalization(FirstOrder_spec,spec_raw, method='simple'):
        if 'simple' in method:
            indx_norm = SpectraInfo.ramanshift_slice_indx(FirstOrder_spec.spec.ramanshift,'normalization')
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(spec,'normalization'))
            normalization_intensity  = FirstOrder_spec.blcorr_desp_intensity[indx_norm].max()
            
        elif 'fit' in method:
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(FirstOrder_spec,'1st_order'))
            normalization = NormalizeFit(FirstOrder_spec,plotprint = False)
            normalization_intensity = normalization['IG']
            
        norm_dict = {'norm_factor' : 1/normalization_intensity, 
                     'norm_method' : method, 'ramanshift' : spec_raw.ramanshift}
        int_fields = [i for i in spec_raw._fields if 'intensity' in i]
        extra_info_flds = [i for i in spec_raw._fields if i not in int_fields]
        
        _norm_int = {i : getattr(spec_raw, i)/normalization_intensity for i in int_fields}
        norm_dict = {**norm_dict,**spec_raw.info, **_norm_int }
        # [norm_dict.update({i : getattr(spec_raw,i)}) for i in extra_info_flds]
        
        norm_info = namedtuple('norm_info','norm_factor norm_method')
        NormSpec = namedtuple('spectrum_normalized', SpectrumTemplate().template._fields + norm_info._fields)(**norm_dict)
        return NormSpec
    
    def __repr__(self):
        return f'{self.__class__.__name__}, {repr(self.spec)}'


class SpectrumMethods:
    
    data = SpecTemplate
    
    def __init__(self, ramanshift, intensity, label = '', **kwargs):
        self.ramanshift = ramanshift
        self.intensity = intensity
        self.label = label
        self.kwargs = kwargs




class SpectrumSplitter(SpectrumMethods):
    
    # def __init__(self, *args, **kws):
        # super().__init__(*args, **kws)
    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
    
    def split_data(self):

        _r,_int = self.ramanshift,self.intensity
        # self.register.get(on_lbl)
        _d = {}
        
        for windowname, limits in SpectrumWindows().items():
            ind = (_r >= np.min(limits)) & (_r <= np.max(limits))
            _intslice = _int[ind]
            label = f'window_{windowname}'
            if self.label:
                label = f'{self.label}_{label}'
            _data = self.data(_r[ind], _int[ind], label )
            setattr(self,label, _data)
            _d.update(**{windowname : _data})
        self.windows_data = _d
        
    # def __iter__(self):
        
            # self.register_spectrum(_r, _intslice, label)
class Filter(SpectrumMethods):
    
      def get_filtered(intensity):
#        fltrd_spec = self.raw_spec
        int_savgol_fltr = signal.savgol_filter(intensity, 13, 3, mode='nearest')
#        fltrd_spec._replace(intensity=int_savgol_fltr)
        return int_savgol_fltr

class BaselineSubtractorNormalizer(SpectrumSplitter):
    
    
    def __init__(self, *args, **kws):
        super().__init__(*args, **kws)
        self.split_data()
        self.windowlimits = SpectrumWindowLimits()
        self.subtract_loop()
        self.get_normalization_factor()
        self.set_normalized_data()
    
    def subtract_loop(self):
        
        _blcorr = {}
        _info = {}
        for windowname, spec in self.windows_data.items():
            
            blcorr_int, blcorr_lin = self.subtract_baseline_per_window(windowname, spec)
            label = f'blcorr_{windowname}'
            if self.label:
                label = f'{self.label}_{label}'
            
            _data = self.data(spec.ramanshift, blcorr_int, label )
            _blcorr.update(**{windowname : _data})
            _info.update(**{windowname : blcorr_lin})
        self.blcorr_data = _blcorr
        self.blcorr_info = _info
    
    
    def subtract_baseline_per_window(self, windowname, spec):
        rs = spec.ramanshift
        
        if windowname.startswith('full'):
            i_fltrd_dspkd_fit = self.windows_data.get('1st_order').intensity
        else:
            i_fltrd_dspkd_fit = spec.intensity
        
        _limits = self.windowlimits.get(windowname)
        assert bool(_limits),f'no limits for {windowname}'
        
        bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:_limits[0]]),np.mean(i_fltrd_dspkd_fit[_limits[1]::])])
        i_blcor = spec.intensity - (bl_linear[0]*rs+bl_linear[1])
#        blcor = pd.DataFrame({'Raman-shift' : w, 'I_bl_corrected' :i_blcor, 'I_raw_data' : i})
        return i_blcor,bl_linear
    
    def get_normalization_factor(self, norm_method = 'simple'):
        
        if norm_method == 'simple':
            normalization_intensity  = np.nanmax(self.blcorr_data['normalization'].intensity)
            
        elif norm_method == 'fit':
            normalization = NormalizeFit(FirstOrder_spec,plotprint = False)
            normalization_intensity = normalization['IG']
            
        self.norm_factor = 1/normalization_intensity
        norm_dict = {'norm_factor' : self.norm_factor, 'norm_method' : norm_method}
        self.norm_dict = norm_dict
    
    def set_normalized_data(self):
        
        _normd = {}
        for windowname, spec in self.blcorr_data.items():
            
            label = f'norm_blcorr_{windowname}'
            if self.label:
                label = f'{self.label}_{label}'
            
            _data = self.data(spec.ramanshift, spec.intensity*self.norm_factor, label )
            _normd.update(**{windowname : _data})
        self.norm_data = _normd
    
        # if windowname in ['1st_order','full', 'full_1st_2nd']:
        #     _limits = (20,-20)
        # elif windowname == '2nd_order':
        #     _limits = (5,-5)
        # else:
        #     _limits = (10,-10)
        #     bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:20]),np.mean(i_fltrd_dspkd_fit[-20::])])
        # elif windowname == '2nd_order':
        #     bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:5]),np.mean(i_fltrd_dspkd_fit[-5::])])
        # else:
        #     bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:10]),np.mean(i_fltrd_dspkd_fit[-10::])])

class Normalizer(SpectrumMethods):
    
     def normalization(FirstOrder_spec,spec_raw, method='simple'):
        if 'simple' in method:
            indx_norm = SpectraInfo.ramanshift_slice_indx(FirstOrder_spec.spec.ramanshift,'normalization')
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(spec,'normalization'))
            normalization_intensity  = FirstOrder_spec.blcorr_desp_intensity[indx_norm].max()
            
        elif 'fit' in method:
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(FirstOrder_spec,'1st_order'))
            normalization = NormalizeFit(FirstOrder_spec,plotprint = False)
            normalization_intensity = normalization['IG']
            
        norm_dict = {'norm_factor' : 1/normalization_intensity, 
                     'norm_method' : method, 'ramanshift' : spec_raw.ramanshift}
        int_fields = [i for i in spec_raw._fields if 'intensity' in i]
        extra_info_flds = [i for i in spec_raw._fields if i not in int_fields]
        
        _norm_int = {i : getattr(spec_raw, i)/normalization_intensity for i in int_fields}
        norm_dict = {**norm_dict,**spec_raw.info, **_norm_int }
        # [norm_dict.update({i : getattr(spec_raw,i)}) for i in extra_info_flds]
        
        norm_info = namedtuple('norm_info','norm_factor norm_method')
        NormSpec = namedtuple('spectrum_normalized', SpectrumTemplate().template._fields + norm_info._fields)(**norm_dict)
        return NormSpec


def array_nan_checker(array):
    _nans = [n for n,i in enumerate(array) if np.isnan(i)]
    return _nans

#
class Despiker(SpectrumMethods):
    '''
    A Despiking algorithm from reference literature: https://doi.org/10.1016/j.chemolab.2018.06.009.
    
    Parameters
    ----------
    input_intensity : np.ndarray
        The intensity array of which the desipked intensity will be calculated.
    info : dict, optional
        Extra information from despiking settings are added to this dict.
    
    
    
    Attributes
    ---------
    despiked_intensity : np.ndarray
        The resulting array of the despiked intensity of same length as input_intensity.
    
    Notes
    --------
    Let Y1;...;Yn represent the values of a single Raman spectrum recorded at equally spaced wavenumbers.
    From this series, form the detrended differenced seriesr Yt ...:This simple
    ata processing step has the effect of annihilating linear and slow movingcurve linear trends, however,
    sharp localised spikes will be preserved.Denote the median and the median absolute deviation of 
    D.A. Whitaker, K. Hayes. Chemometrics and Intelligent Laboratory Systems 179 (2018) 82–84
    '''
    
    
    def __init__(self,input_intensity, Z_threshold = 20, info = {}):
        self.info = info
        self.Z_threshold = Z_threshold
        self.input_intensity = copy.deepcopy(input_intensity)
        
        # self.check_input_intensity()
       

    @property
    def input_intensity(self):
        return self._input_intensity

    @input_intensity.setter
    def input_intensity(self, value):
        _int = value
        type_test = str(type(_int))
        if '__main__' in type_test:
            if 'intensity' in test._fields:
                int_used = test.intensity
        elif 'numpy.ndarray' in type_test:
            int_used = _int
        elif 'dict' in type_test:
            int_used = test.get([i for i in test.keys() if 'intensity' in i][0])
        else:
            raise ValueError(f'Despike input error {type_test} for {value}')

        self.info.update({'input_type' : type_test})
        self._input_intensity = int_used
        self.run_despike()
    
    def run_despike(self):
        self.calc_Z()
        self.calc_Z_filtered()
        self.apply_despike_filter()
        self.pack_to_df()
    
   
   # TODO still finish...
    def calc_Z(self): 
#        y = intensity[Ystr]
        intensity = self.input_intensity
        dYt = np.append(np.diff(intensity),0)
        #    dYt = intensity.diff()
        dYt_Median = np.median(dYt)
        #    M = dYt.median()
        #    dYt_M =  dYt-M
        dYt_MAD = np.median(abs(dYt - dYt_Median))
        #    MAD = np.mad(dYt)
        Z_t = (0.6745*(dYt-dYt_Median)) / dYt_MAD
        #    intensity = blcor.assign(**{'abs_Z_t': Z_t.abs()})
        self.Z_t =  Z_t
    
    def calc_Z_filtered(self):
        Z_t_filtered = copy.deepcopy(self.Z_t)
        Z_t_filtered[np.abs(self.Z_t) > self.Z_threshold] = np.nan
        Z_t_filtered[0] = Z_t_filtered[-1] = 0
        self.Z_t_filtered = Z_t_filtered
        self.info.update({'Z_threshold' : self.Z_threshold})
#        Z_threshold = 3.5
#        Z_t_filtered = [Z_t
#        Z_t_filtered[Z_filter_indx] = np.nan
#        y_out,n = intensity,len(intensity)
    
    def apply_despike_filter(self, ma=5, ignore_lims=(20,46)):
        intensity,Z_t_filtered = copy.deepcopy(self.input_intensity), self.Z_t_filtered
        n = len(intensity)
        i_despiked = intensity
        spikes = np.where(np.isnan(Z_t_filtered))
        for i in list(spikes[0]):
            
            if i < ignore_lims[0] or i > ignore_lims[1]:
                w = np.arange(max(1,i-ma),min(n,i+ma))
                w = w[~np.isnan(Z_t_filtered[w])]
                i_despiked[i] = np.mean(intensity[w]) 
            else:
                pass # ignored
        self.info.update({'Z_filter_ma' : ma})
        self.despiked_intensity = i_despiked
        
    def pack_to_df(self):
        cols =  [self.input_intensity, self.Z_t, self.Z_t_filtered, self.despiked_intensity] 
        names = ['input_intensity','Zt', 'Z_t_filtered','despiked_intensity']
        _d = dict(zip(names,cols))
        self.dict = _d
        self.df = pd.DataFrame(_d)
    
    def plot_Z(self):
        # fig,ax = plt.subplots(2)
        self.df.plot(y=['Zt', 'Z_t_filtered'],alpha=0.5)
        self.df.plot(y=['input_intensity','despiked_intensity'],alpha=0.5)
        # plt.show()
        # plt.close()
