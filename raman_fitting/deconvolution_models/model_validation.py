#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:08:26 2021

@author: zmg
"""

import inspect
import sys

import matplotlib.pyplot as plt
import pandas as pd

from lmfit import Parameters

from raman_fitting.deconvolution_models.base_peak import BasePeak
import raman_fitting.deconvolution_models.first_order_peaks as first_order_peaks
import raman_fitting.deconvolution_models.second_order_peaks as second_order_peaks



class Peak_Collection():
    '''
    This class collects all BasePeak type classes, which are costum lmfit type models, and 
    constructs an iterable collection of all defined.
    '''
    _bad_models = []
    _standard_modules = [first_order_peaks, second_order_peaks]
    _base_model = BasePeak
    standard_model_selection = []
    _skip_models = []
    _Randles_models = []
    
    def __init__(self, endwsith = '_peak'):
        # self.model_prefixes = model_prefixes
        self._endswith = endwsith
        
        self.model_constructor()
    
    # @property
    # def lmfit_models(self):
    #     return self.lmfit_models
    
    # @lmfit_models.getter(self):
    # def lmfit_models(self):
    
    def model_constructor(self):
        self.find_inspect_models()
        self.validation_inspect_models()
        
        self.model_selector()
        
        self.extra_assignments()
      
        
    
    def find_inspect_models(self):
        self._inspect_models = [a for i in (inspect.getmembers(mod, inspect.isclass) for mod in self._standard_modules)
                                for a in i if issubclass(a[1],self._base_model) and a[1] is not self._base_model]
        assert self._inspect_models, 'inspect.getmembers found 0 models, change the search parameters for _standard_modules or _base_model'

    def validation_inspect_models(self):
            # i for i in (inspect.getmembers(mod, inspect.isclass) for mod in self._standard_modules)
                                            # if issubclass(i,BasePeak)]
        _validmods,_badfuncs = [],[]
        for _nm,m in  self._inspect_models:
            try:
                _inst = m()
                if hasattr(_inst,'model'):
                    _validmods.append(m)
            except Exception as e:
                _badfuncs.append(m)
        self.valid_models = _validmods
        self.bad_funcs = _badfuncs
    
    def model_selector(self):
        self.model_selection = [m for m in self.valid_models ]
        self._skipped_models = set(self._bad_models + self._skip_models)
        if self.standard_model_selection:
            self.model_selection = [m for m in self.valid_models if not m().name in self._skipped_models]   
        if self._endswith:
            self.model_selection = [m for m in self.valid_models 
                                    if (m().name.endswith(self._endswith) and not m().name in self._skipped_models)]   
    
    def extra_assignments(self):
        self.assign_colors_to_mod_inst()
        self.add_model_names_var_names()
        # self.add_standard_init_params()
        self.set_options()
    
    def assign_colors_to_mod_inst(self):
        self.cmap_set = plt.get_cmap('Dark2' if not len(self.model_selection) > 10 else 'tab20')
        _mod_inst = []
        for n,m in enumerate(self.model_selection):
            _m_inst = m()
            _m_inst.color =  ', '.join([str(i) for i in self.cmap_set(n)])
            # _m_inst._funcname = str(m).split('__main__.')[-1][:-2]
            _m_inst._lenpars = len(_m_inst.model.param_names)
            _mod_inst.append(_m_inst)
        _mod_inst = sorted(_mod_inst, key= lambda x: x._lenpars)
        self.lmfit_models = _mod_inst
    
    def add_standard_init_params(self):
        self.standard_init_params = Parameters()
        self.standard_init_params.add_many(*BasePeak._params_guesses_base)
        
    def add_model_names_var_names(self):
        _modvars = {i.model.name : i.model.param_names for i in self.lmfit_models}
        self.modpars = _modvars
        
    def get_df_models_parameters(self):
        _models = pd.DataFrame([(i.model.name,len(i.model.param_names),', '.join(i.model.param_names))
                                    for i in self.lmfit_models],columns=['Model_EEC','model_lenpars','model_parnames'])
        return _models

    def set_options(self):
        _options = {i.__class__.__name__ : i for i in self.lmfit_models}
        
        self.model_dict = _options
        self.options = _options.keys()
    
    def get_dict(self):
        return {i.__module__+', '+i.__class__.__name__ : i  for i in self.lmfit_models}
    
    
    def __getattr__(self, name):

        if name in self.options:
            return self.model_dict.get(name, None)
        elif 'normalization' in name:
            return self.normalization_model()
        else:
            raise AttributeError(f'Chosen name "{name}" not in in options: "{", ".join(self.options)}".')
    
    def normalization_model(self):
        _D_norm = first_order_peaks.D_peak(normalization=True)
        _G_norm = first_order_peaks.G_peak(normalization=True) 
        norm_mod = _D_norm.model + _G_norm.model
        return norm_mod
    
    def __iter__(self):
        for mod_inst in self.lmfit_models:
            yield mod_inst
        # self.params_set = set([a for m in self.lmfit_models for a in m[1].param_names])
#    lmfit_models = [Model(i.func,name=i.name) for i in model_selection]
    def __repr__(self):
        return f'Model Collections, {len(self.model_selection)} models from endswith {self._endswith}: '+'\n\t- '+'\n\t- '.join([f'{i.model} \t "{i.__class__.__name__}" in "{i.__module__}", {i._lenpars}' for i in self.lmfit_models])
    
