#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:08:26 2021

@author: zmg
"""

import inspect
from warnings import warn


import matplotlib.pyplot as plt
import pandas as pd

from lmfit import Parameters

if __name__ == '__main__':
    from base_peak import BasePeak
    import first_order_peaks 
    import second_order_peaks 
else:
    from .base_peak import BasePeak
    from . import first_order_peaks 
    from . import second_order_peaks 

class NotFoundAnyModelsWarning(UserWarning):
    pass

#%%
class PeakModelValidator():
    '''
    This class collects all BasePeak type classes, which are costum lmfit type models, and 
    constructs an iterable collection of all defined.
    '''
    _bad_models = []
    _standard_modules = [first_order_peaks, second_order_peaks]
    _base_model = BasePeak
    standard_model_selection = []
    _skip_models = []

    def __init__(self, endwsith = '_peak'):
        # self.model_prefixes = model_prefixes
        self._endswith = endwsith
        
        self._inspect_models = []
        self.find_inspect_models()
        
        self.valid_models = set()
        self._invalid_models = set()
        self.validation_inspect_models()
        
        self._skipped_models = {}
        self.selected_models = []
        self.model_selector()
        
        # self.model_constructor()
        self.lmfit_models = []
        self.extra_assignments()

    def find_inspect_models(self):
        self._inspect_modules_all = self._base_model.__subclasses__()
        # [cl for i in (inspect.getmembers(mod, inspect.isclass) 
                                # for mod in self._standard_modules)
                                     # for cl in i]
        
        self._inspect_models = [a for a in self._base_model.__subclasses__()
                                if issubclass(a,self._base_model) 
                                and a is not self._base_model]
        if not self._inspect_modules_all:
            warn(f'\nNo classes were found in inspected modules:\n {", ".join(self._standard_modules)}\n', NotFoundAnyModelsWarning)
        elif not self._inspect_models:
            warn(f'\nNo base models were found in:\n {", ".join([str(i) for i in self._inspect_modules_all])}.\n', NotFoundAnyModelsWarning)
        # assert self._inspect_models, 'inspect.getmembers found 0 models, change the search parameters for _standard_modules or _base_model'

    def validation_inspect_models(self):
        for m in  self._inspect_models:
            try:
                _inst = m()
                if hasattr(_inst,'model'):
                    if getattr(_inst, 'model'):
                        self.valid_models.add(m)
                    else:
                        self._invalid_models.add((m,'instance model attr is None'))
                else:
                    self._invalid_models.add((m,'instance model has no attr model'))
            except Exception as e:
                self._invalid_models.add((m,f'Exception: {e}'))
    
    def model_selector(self):
        self.selected_models = [m for m in self.valid_models]
        self._skipped_models = set(self._bad_models + self._skip_models)
        if self.standard_model_selection:
            self.selected_models = [m for m in self.valid_models if not m().name in self._skipped_models]   
        if self._endswith:
            self.selected_models = [m for m in self.valid_models 
                                    if (m().name.endswith(self._endswith) and not m() in self._skipped_models)]   
    
    def extra_assignments(self):
        self.options = ()
        if self.selected_models:
            self.assign_colors_to_mod_inst()
            self.add_model_names_var_names()
        # self.add_standard_init_params()
            
            self.set_options()
    
    def assign_colors_to_mod_inst(self):
        self.cmap_set = plt.get_cmap('Dark2' if not len(self.selected_models) > 10 else 'tab20')
        for n,m in enumerate(self.selected_models):
            _m_inst = m()
            _m_inst.color =  ', '.join([str(i) for i in self.cmap_set(n)])
            # _m_inst._funcname = str(m).split('__main__.')[-1][:-2]
            _m_inst._lenpars = len(_m_inst.model.param_names)
            self.lmfit_models.append(_m_inst)
        self.lmfit_models= sorted(self.lmfit_models, key= lambda x: x._lenpars)
        # self.lmfit_models = _mod_inst
    
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
        # raise AttributeError(f'Chosen name "{name}" not in in options: "{", ".join(self.options)}".')
        
        try:
            _options = self.__getattribute__('options')
            
            if name in _options:
                return self.model_dict.get(name, None)
            raise AttributeError(f'Chosen name "{name}" not in options: "{", ".join(_options)}".')
        except AttributeError:
            # if 'normalization' in name:
                # return self.normalization_model()
            raise AttributeError(f'Chosen name "{name}" not in attributes')
        
        # else:
            # raise AttributeError(f'Chosen name "{name}" not in in options: "{", ".join(self.options)}".')
    
    def normalization_model(self):
        pass  # TODO separate peaks in groups
    
    def __iter__(self):
        for mod_inst in self.lmfit_models:
            yield mod_inst
        # self.params_set = set([a for m in self.lmfit_models for a in m[1].param_names])
#    lmfit_models = [Model(i.func,name=i.name) for i in model_selection]
    def __repr__(self):
        return f'Model Collections, {len(self.selected_models)} models from endswith {self._endswith}: '+'\n\t- '+'\n\t- '.join([f'{i.model} \t "{i.__class__.__name__}" in "{i.__module__}", {i._lenpars}' for i in self.lmfit_models])
    
