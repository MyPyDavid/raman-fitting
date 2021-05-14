#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  8 10:17:17 2021

@author: dw
"""


from raman_fitting.deconvolution_models.model_validation import Peak_Collection

# ====== MODEL CHOICE ======= #


class InitializeModels():
    ''' 
    This class will initialize and validate the different fitting models.
    The models are of type lmfit.model.CompositeModel and stored in a dict with names
    for the models as keys.
    '''
    
    peak_collection = Peak_Collection()
    _standard_1st_order = {'2peaks' : 'G+D',
                            '3peaks' : 'G+D+D3',
                            '4peaks' : 'G+D+D3+D4',
                            '5peaks' : 'G+D+D2+D3+D4',
                            '6peaks' : 'G+D+D2+D3+D4+D5'}
    
    _standard_2nd_order = {'2nd_4peaks' : 'D4D4+D1D1+GD1+D2D2'}

                   
    def __init__(self, standard_models = True):
        self.construct_standard_models()    
        self.normalization_model = self.peak_collection.normalization
        
    def construct_standard_models(self):
        
        _models = {}
        
        _models_1st = {f'1st_{key}+Si' : BaseModel(peak_collection = self.peak_collection, model_name=value) 
                       for key,value in self._standard_1st_order.items()}
        _models.update(_models_1st)
        _models_1st_no_substrate = {f'1st_{key}' : BaseModel(peak_collection = self.peak_collection, model_name=value, add_substrate=False, substrate_peak='')
                                    for key,value in self._standard_1st_order.items()}
        _models.update(_models_1st_no_substrate)
        self.first_order = {**_models_1st, **_models_1st_no_substrate}
        
        
        _models_2nd = {key : BaseModel(peak_collection = self.peak_collection, model_name=value, add_substrate=False, substrate_peak='')
                       for key,value in self._standard_2nd_order.items()}
        _models.update(_models_2nd)
        self.second_order = _models_2nd
        
        self.all_models = _models




class BaseModel():
    ''' This Model class combines the peaks from BasePeak into a regression model of type lmfit.model.CompositeModel
        that is compatible with the lmfit Model and fit functions.
    '''
    
    model_prefix_name = ''
    
    def __init__(self, peak_collection = Peak_Collection(), model_name = '', add_substrate = True, substrate_peak = 'Si1_peak'):
        self.peak_collection = peak_collection
        self._model_name = model_name
        self._add_substrate = add_substrate
        self.substrate_peak = substrate_peak
        
        self.model_constructor()
        # self.peak_dict = self.peak_collection.get_dict()
        
    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, name):
        '''Calls the model constructer on the model_name'''
        self._model_name = name
        self.model_constructor()
    
    @property
    def add_substrate(self):
        return self._add_substrate
    
    @add_substrate.setter
    def add_substrate(self, value : bool):
        _hasattr_model = hasattr(self, 'model')
        if _hasattr_model and value:
            self.add_substrate_to_model()    
        elif _hasattr_model and not value:
            self.model_constructor()
            
        elif not _hasattr_model and value:
            self.model_constructor()
            self.add_substrate_to_model()
        else:
            self.model_constructor()
            
    def add_substrate_to_model(self):
        if hasattr(self,'model'):
            self.model_raw = self.model
            if not any([i.prefix[:-1] in self.substrate_peak for i in self.model.components]):
                self.model = self.model_raw + getattr(self.peak_collection, self.substrate_peak).model
        
    def model_constructor(self):
        
        if type(self._model_name) == str:
            _splitname = self._model_name.split('+')
            assert _splitname, f'Chose name for model is empty {self.name}'
            _mod = []
            for pname in _splitname:
                pname
                _match = [_pk for _pk in self.peak_collection.options if any(pname == _p for _p in _pk.split('_'))]
                if _match:
                    if len(_match) == 1:
                        if _match[0] in self.substrate_peak and not self.add_substrate:
                            raise ValueError(f'Substrate peak included in { self._model_name}, however add_substrate is {self.add_substrate}')
                        _mod.append(_match[0])
            self.mod_lst = _mod
            self.eval_mod_str()
            if self.add_substrate:
                self.add_substrate_to_model()
                
        
        if hasattr(self, 'model'):
            self.model_prefix_name = '+'.join([i.prefix[:-1] for i in self.model.components])
        
    def eval_mod_str(self):
        if self.mod_lst:
            _mod_str = ' + '.join([f'self.peak_collection.{peak}.model' for peak in self.mod_lst])
            try:
                _model = eval(_mod_str)
                self.model = _model
            except Exception as e:
                print(f'Exception in eval of model string {_mod_str}:\n{e}')
                raise e
                
    def __repr__(self):
        _txt = f'{self.model_prefix_name}: '
        if hasattr(self,'model'):
            _txt += repr(self.model)    
        else:
            _txt += 'empty model'
        return _txt
    
    

    