#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:54:49 2021

@author: zmg
"""

import inspect
import operator

from abc import ABC, abstractmethod

from lmfit.models import VoigtModel,LorentzianModel, GaussianModel

from lmfit import CompositeModel


class BasePeak(ABC):
    '''Base class for typical intensity peaks found the raman spectra.\
    Several peaks combined are used as a model (composed in the fit_models module)\
        to fit a certain region of the spectrum.'''
    
    peak_type_options = ['Lorentzian', 'Gaussian', 'Voigt']
    model = None
        
    def __init__(self, peak_type = 'Lorentzian', peak_name ='prefix', 
                 gammavary :bool = False , normalization : bool = False):

        self._peak_type = peak_type
        self._peak_name = peak_name
        
        self._normalization = normalization
        self._gammavary = gammavary
        
        self.type_to_model_chooser()
        self.assign_settings_to_params()
        self.make_model_hints()
        
    def __getattr__(self, name):
        
        if name == 'name':
            return self.__class__.__name__
        elif name == 'module':
            return self.__module__
    
    
    @property
    def peak_type(self):
        '''The peak type property should be in {self.peak_type_options}. '''
        return self._peak_type
    
    @peak_type.setter
    def peak_type(self, value: str):
        if value in self.peak_type_options:
            self._peak_type = value
            self.type_to_model_chooser()
        else:
            raise ValueError(f'The value "{value}" for "peak_type" is not in {self.peak_type_options}.')
        
    @property
    def peak_name(self):
        '''This is the name that the peak will get as prefix'''
        return self._peak_name
    
    @peak_name.setter
    def peak_name(self, value : str, maxlen = 10):
        if len(value) < 10:
            self._peak_name = value
            self.type_to_model_chooser()
        else:
            raise ValueError(f'The value "{value}" for peak_name is too long({len(value)}) (max. {maxlen}).')
            
    
    @property
    @abstractmethod
    def input_param_settings(self):
        # TODO maybe read in param settings form eg xls file
        param_settings = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        return param_settings
    
    
    @property
    def normalization(self):
        ''' The normalization = True only for internal code purposes.
        Optional param_settings and only used to make the normalization of the spectra.
        '''
        return self._normalization
    
    @normalization.setter
    def normalization(self, value):
        ''' Check if normalization is True that the param settings are there'''
        if value and not self.normalization_param_settings:
            raise ValueError('When normalization is set True there should be a valid parameters setting')
        elif value and self.normalization_param_settings:
            self.assign_settings_to_params()
        elif not value:
            pass
        else:
            pass
        self._normalization = value
    
    # @classmethod
    def normalization_param_settings(self):
        return {}
    
    @property
    def gammavary(self):
        return self._gammavary
        
    @normalization.setter
    def gammavary(self, value):
        ''' Check if True that the settings are there'''
        if value and not self.gammavary_settings():
            raise ValueError('When gammavary is set True there should be a valid parameters setting')
        elif not value:
            self._gammavary = value
        else:
            pass
   
    def gammavary_settings(self):
        return {'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : self._gammavary}}
    
    def assign_settings_to_params(self):
        
        settings = self.input_param_settings()
        if self.normalization:
             settings = self.normalization_param_settings()
        if self.gammavary:
            settings.update(self.gammavary_settings())
        self.param_hints = settings
    
    
    def type_to_model_chooser(self):
        
         if self._peak_type and self._peak_name:
            prefix_set = self._peak_name + '_'
            if 'Lorentzian' in self._peak_type:
                model = LorentzianModel(prefix=prefix_set)
            elif 'Gaussian' in self._peak_type:
                model = GaussianModel(prefix=prefix_set)
            elif 'Voigt' in self._peak_type:
                model = VoigtModel(prefix=prefix_set)
                        
            self.model = model

    def make_model_hints(self):
        if self.model:
            try:
                for pname,pars in self.param_hints.items():
                    try:
                        self.model.set_param_hint(pname,**pars)
                    except Exception as e:
                        _error = f'Error in make_model_hints, check param_hints for {pname} with {pars}'
                        
            except Exception as e:
                _error = f'Error in make_model_hints, check param_hints'
    
    
    @classmethod
    def getfile(cls):
        return inspect.getfile(cls)
    
    @classmethod
    def getmodule(cls):
        return inspect.getmodule(cls)
    
    def __repr__(self):
        
        _name =  self.__class__.__name__
        
        _repr = f'{_name}'
        if self.model:
            _repr += f', {self.model.name}'
        
            _param_center = self.model.param_hints.get('center', {})
            if _param_center:
                _center_txt = ''
                _center_val = _param_center.get('value')
                _center_min = _param_center.get('min',_center_val)
                if _center_min != _center_val:
                    _center_txt += f'{_center_min} < '
                
                _center_txt += f'{_center_val}'
                _center_max = _param_center.get('max', _center_val)
                if _center_max != _center_val:
                    _center_txt += f' > {_center_max}'
                _repr += f', center : {_center_txt}'
        else:
            _repr += ': no Model set'
            
        return _repr
        
    def print_params(self):
        if self.model:
            self.model.print_param_hints()
            
    # def __add__(self, added_peak):
    #     assert issubclass(added_peak.__class__,(ABC, BasePeak))
    #     # assert type(added_peak) == type(self)
    #     if hasattr(added_peak,'model'):
    #         return CompositeModel(self.model, added_peak.model, operator.add)
        

class test_peak(BasePeak):
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='test', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
    
    def input_param_settings(self):
        # TODO maybe read in param settings form eg xls file
        param_settings = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        param_settings = {}
        return param_settings
    
    def normalization_param_settings(self):
        settings = {'center' : {'value' : 1581, 'min' : 1500, 'max' : 1600},
                    'sigma' : {'value' : 40, 'min' : 1E-05, 'max' : 1E3},
                    'amplitude' : {'value' : 8E4, 'min' : 1E2}}
        return settings


 

class test_peak2(BasePeak):
    
    def __init__(self, peak_type = 'Gaussian', peak_name ='t2', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
    
    def input_param_settings(self):
        # TODO maybe read in param settings form eg xls file
        param_settings = {'center' : {'value' : 1271,'min' : 1245, 'max' : 1295},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        param_settings = {}
        return param_settings
    
    def normalization_param_settings(self):
        settings = {'center' : {'value' : 1281, 'min' : 1100, 'max' : 1600},
                    'sigma' : {'value' : 42, 'min' : 1E-05, 'max' : 1E3},
                    'amplitude' : {'value' : 8E4, 'min' : 1E2}}
        return settings




def _test_add():
    bp1 = test_peak()
    bp2 = test_peak2()
    bp1+bp2


def _testing():
    bp = BasePeak()
    bp.peak_type = 'Cheese' # error
    bp.peak_type = 'Voigt'
    
    bp.peak_name = 'pre'*100 # error
    bp.model.name
    
    # updating name and model
    bp.peak_name = 'G'
    bp.model.name
    bp.peak_type = 'Lorentzian'
    bp.model.name
    
    help(bp)

def _testing_class(classname):
    bp = classname()
    try:
        bp.peak_type = 'Cheese' # error
    except Exception as e:
        print('Error 1:', e)
    bp.peak_type = 'Voigt'
    
    try:
        bp.peak_name = 'pre'*100 # error
    except Exception as e:
        print('Error 2:', e)
    bp.model.name
    
    # updating name and model
    bp.peak_name = 'G'
    print(f'Model name: {bp.model.name}')
    bp.peak_type = 'Lorentzian'
    print(f'Model name: {bp.model.name}')
    bp.model.name
    return bp 
    
def _testing_func():
    bp = _testing_class(test_peak)
    
    bp2 = _testing_class(test_peak(peak_name='ADD'))
    
