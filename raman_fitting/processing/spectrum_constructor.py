#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 11:10:59 2021

@author: zmg
"""

import copy
from collections import namedtuple
from typing import Dict, List


from pathlib import Path
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from raman_fitting.processing.cleaner import Filter,Despiker, BaselineSubtractorNormalizer
from raman_fitting.processing.spectrum_template import SpectrumWindows, SpecTemplate


def _testing():
    spectrum_data = SpectrumDataLoader(file = meannm[-1], run_kwargs = _spectrum_position_info_kwargs, ovv = meangrp)
    self = spectrum_data
    self._despike.Z_t
    self._despike.input_intensity
    
    self = self._despike

@dataclass(order = True, frozen = False)
class SpectrumDataLoader():
    '''Raman Spectrum Dataclass, reads in the file and constructs a spectrum from the data.'''
    
    _fields = ('ramanshift', 'intensity')
    
    # _spectrum_grp_cols = ['PAR_file','Segment #',EvRHE, 'RPM_DAC']
    
    
    file: Path = field(default=Path(Path.cwd().joinpath('empty.txt'))) 
    # sample_position: int = 0
    
    # ramanshift: np.array = field(default=np.array([]), init=False)
    # intensity: np.array = field(default=np.array([]), init=False)
    spectrum_length: int = field(default=0, init=False)
    
    info : Dict = field(default_factory=dict,repr=False)
    # data : type(pd.DataFrame) = field(default=pd.DataFrame(),repr=False)
    ovv : type(pd.DataFrame) = field(default=pd.DataFrame(),repr=False)
    run_kwargs : Dict = field(default_factory=dict,repr=False)
    
    def __post_init__(self):
#        self.E_dc_RHE = np.round(self.E_dc_RHE, 3)
        self.register = {}
        self.load_data_delegator()
    
    def register_spectrum(self,ramanshift,intensity, label):
        _spec = SpecTemplate(ramanshift,copy.deepcopy(intensity), label)
        self.register.update({label : _spec})
    
    def __getattr__(self, value):
        
        if value in self.run_kwargs.keys():
            return self.run_kwargs.get(value,None)
        else:
            # super().__getattr__(value) 
            raise AttributeError(f'Attribute "{value}" is not in class.')
            
    def load_data_delegator(self):
        
        self._read_succes = False
        
        if self.file.exists():
            
            self.info = {'FilePath' : self.file}
            
            self.load_data()
            if self._read_succes:
                self.spectrum_methods_delegator()
            
            self.info = {**self.info, **self.run_kwargs}
            
            
        elif self.file.name == 'empty.txt':
            print(f'Default empty.txt File: "{self.file}" ')
        else:
            raise ValueError(f'File: "{self.file}" does not exist.')
    
    def load_data(self, on_lbl = 'raw'):
        # assert self.file.exists(), f'File: "{self.file}" does not exist.'
        ramanshift, intensity= np.array([]),np.array([])
        i = 0
        while not ramanshift.any() and i < 2000:
            try:
                ramanshift, intensity = np.loadtxt(self.file, usecols=(0, 1), delimiter='\t', unpack=True, skiprows=i)
                
                # Alternative parsing method with pandas.read_csv
                # _rawdf = pd.read_csv(self.file, usecols=(0, 1), delimiter='\t', 
                #                     skiprows=i, header =None, names=['ramanshift','intensity'])
                print(self.file, len(ramanshift),len(intensity))
                self._skiprows = i
                self._read_succes = True
                self.spectrum_length = len(ramanshift)
                self.info.update({'spectrum_length' : self.spectrum_length})
            except ValueError:
                i += 1
        
        self.register_spectrum(ramanshift, intensity, on_lbl )
        # self.ramanshift = ramanshift
        # self.intensity = intensity
        # self.register_spectrum(ramanshift,)
    
    def spectrum_methods_delegator(self):
        
        self.filter_data(on_lbl = 'raw', out_lbl = 'filtered')
        self.despike(on_lbl ='filtered', out_lbl = 'despiked')
        self.baseline_correction(on_lbl = 'despiked', out_lbl = 'clean_data')
        self.set_clean_data_df()
        self.set_df_from_register()
        
        
    def filter_data(self,on_lbl = 'raw', out_lbl = 'filtered'):
        
        _r,_int,_lbl = self.register.get(on_lbl)
        filtered_intensity = Filter.get_filtered(_int)
        self.filtered_intensity = filtered_intensity 
        self.register_spectrum(_r, filtered_intensity, out_lbl )
        
    def despike(self, on_lbl ='filtered', out_lbl = 'despiked'):
        
        _r,_int,_lbl = self.register.get(on_lbl)
        _despike = Despiker(_int) # TODO check for nan in array
        self._despike = _despike
        self.register_spectrum(_r, _despike.despiked_intensity, out_lbl )
        
        
    def baseline_correction(self,on_lbl = 'despiked', out_lbl = 'clean_data'):
        
        _r,_int,_lbl = self.register.get(on_lbl)
        _baseline_corrected = BaselineSubtractorNormalizer(_r,_int,label='despiked')
        self._baseline_corrected = _baseline_corrected
        
        _fullspec = _baseline_corrected.norm_data['full']
        self.register_spectrum(_fullspec.ramanshift, _fullspec.intensity, out_lbl )
        self.clean_data = _baseline_corrected.norm_data
        
    def set_clean_data_df(self):
        
       self.clean_df = {k : pd.DataFrame({'ramanshift' : val.ramanshift, 
                          f'int_{self.SamplePos}' : val.intensity}) 
                          for k,val in self.clean_data.items()}
    
    def set_df_from_register(self):
        
        _regdf = pd.DataFrame
        for k,val in self.register.items():
            _spec = pd.DataFrame({'ramanshift' : val.ramanshift, 
                          f'{k}_int_{self.SampleID}_{self.SamplePos}' : val.intensity})
            if _regdf.empty:
                _regdf = _spec
            else:
                _regdf = pd.merge_asof(_regdf, _spec, on='ramanshift')
        self.regdf = _regdf
        
    
    def plot_raw(self):
        _raw_lbls = [i for i in self.regdf.columns if not any(a in i for a in ['ramanshift', 'clean_data'])]
        self.regdf.plot(x='ramanshift',y=_raw_lbls)
        
    
    def split_data(self, on_lbl = 'filtered'):

        _r,_int,_lbl = self.register.get(on_lbl)
        for windowname, limits in SpectrumWindows().items():
            ind = (_r >= np.min(limits)) & (_r <= np.max(limits))
            _intslice = _int[ind]
            label = f'{_lbl}_window_{windowname}'
            self.register_spectrum(_r, _intslice, label)
            
            
    
def _testing() :
    self = spectra_collection

class SpectrumDataCollection:
    
    
    MeanSpecTemplate = namedtuple('MeanSpectras' , 'windowname sID_rawcols sIDmean_col mean_info mean_spec')
    
    
    def __init__(self, spectra: List= []):
        self._spectra = spectra
        self._check_members()
        self.test_spectra_lengths()
        self.get_merged_mean_info()
        self.calc_mean()
        
        
    
    def _check_members(self):
        
        assert all(type(spec).__name__ == 'SpectrumDataLoader' for spec in self._spectra )
        assert all(hasattr(spec,'clean_data') for spec in self._spectra)
                   
    def test_spectra_lengths(self):
        lengths = [i.spectrum_length for i in self._spectra]
        set_lengths = set(lengths)
        if len(set_lengths) == 1:
#            print(f'Spectra all same length {set_lengths}')
            pass
        else:
            length_counts = [(i, lengths.count(i)) for i in set_lengths]
            best_guess_length = max(length_counts,key=itemgetter(1))[0]
            print(f'Spectra not same length {length_counts} took {best_guess_length}')
            self._raw_spectra = self._spectra
            
            self._spectra = [spec for spec in self._spectra if spec.spectrum_length == best_guess_length]
            
    def get_merged_mean_info(self):
        
        _d = {} # spec info dict
        _cdks = {} # clean data keys
        _prep_data = {}
        _info_df_lst = []
        for spec in self._spectra:
            if hasattr(spec,'info'):
                if not _d: 
                    _d = spec.info
                else:
                    _d = {x:_d[x] for x in _d if x in spec.info and _d[x] == spec.info[x]}
                
                _info_df_lst.append(spec.info)
                
            
            if hasattr(spec,'clean_data'):
                if not _cdks:
                    _cdks = set(spec.clean_data.keys())
                    
                else:
                    _cdks = {x for x in _cdks if x in set(spec.clean_data.keys())}
                
                if not _prep_data:
                    _prep_data = {key: [(spec.SamplePos, val)] for key,val in  spec.clean_data.items()}
                
                else:
                    for key,val in  spec.clean_data.items():
                        _prep_data.get(key).append((spec.SamplePos, val))
                
                
        _d.update({'mean_spectrum' : True})
        self.prep_clean_data = _prep_data
        self.info = _d       
        self.info_df = pd.DataFrame(_info_df_lst)
  
    
    def calc_mean(self):
        ''' Core function of the merging of spectra of different sample positions'''
        assert hasattr(self,'prep_clean_data')


        _merged_window_specs = {}
        
        _speclst = []
        
        _posmean_lbl_base = f'int_{self.info.get("SampleID")}_mean'
        for wndwnm, data in self.prep_clean_data.items():
            
            
            wndwnm, data 
            _merge_df = pd.DataFrame()
            _pos_lbl_lst = []
            
            for _pos,_sp in data:
                _pos_lbl =f'int_{_pos}' 
                _dfspec = pd.DataFrame({'ramanshift' : _sp.ramanshift, _pos_lbl : _sp.intensity })
                if _merge_df.empty:
                   _merge_df = _dfspec
                else:
                    _merge_df = pd.merge_asof(_merge_df,_dfspec, on='ramanshift')
                _pos_lbl_lst.append(_pos_lbl)
                
            _posmean_lbl = f'{_posmean_lbl_base}_{len(_pos_lbl_lst)}'
            _merge_df = _merge_df.assign(**{_posmean_lbl : _merge_df[_pos_lbl_lst].mean(axis=1)})
            _merged_window_specs.update({wndwnm : _merge_df})
             
            _old_spec = self.MeanSpecTemplate(wndwnm, _pos_lbl_lst, _posmean_lbl, self.info_df,_merge_df )
            _speclst.append(_old_spec)
            
        
        self.fitting_spectra = _speclst
        self.mean_data = _merged_window_specs
        
        # _clean_data = [spec.clean_data for spec in self._spectra]
  
        
    def __repr__(self):
        return f'{self.info}'
    
        
def _testing():
    sp = SpectrumData()
    spcoll = SpectrumDataCollection(sample_spectra)
    self = spcoll

# class SpectrumData():