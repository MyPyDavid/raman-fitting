#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:54:49 2021

@author: dw
"""

import inspect
# import operator
# from abc import ABC, abstractmethod
from lmfit.models import VoigtModel,LorentzianModel, GaussianModel, Model
from lmfit import Parameter,Parameters
# from lmfit import CompositeModel

class BasePeak():
    '''Base class for typical intensity peaks found the raman spectra.\
    Several peaks combined are used as a model (composed in the fit_models module)\
        to fit a certain region of the spectrum.'''

    _keywords = ['peak_name','peak_type','settings']

    PEAK_TYPE_OPTIONS = ['Lorentzian', 'Gaussian', 'Voigt']
    default_settings = {'gamma': 
                             {'value': 1,
                              'min': 1E-05,
                              'max': 70,
                              'vary': False}
                         }
    _intern = list(super.__dict__.keys())+['__module__','_kwargs']
    # input_param_settings = {}
    def __init__(self, *args, **kwargs):
        self._kwargs = kwargs
        self.name = self.__name__
        
        self.model = None
        self.peak_name = 'default'
        self.peak_type = 'Lorentzian'
        self.input_param_settings = {}
        
        allowed_keys = [i for i in dir(self) 
                        if "__" not in i 
                        and any([j.endswith(i) for j in self.__dict__.keys()])
                        and i not in self._intern]
        
         # get a list of all predefined values directly from __dict__
        # Update __dict__ but only for keys that have been predefined 
        # (silently ignore others)
        # To NOT silently ignore rejected keys
        rejected_keys = set(kwargs.keys()) - set(allowed_keys)
        if rejected_keys:
            raise ValueError(f"Invalid arguments in constructor:{rejected_keys}")
        for key, value in kwargs.items():
            # Update properties, but only for keys that have been predefined 
            # (silently ignore others)
            if key in allowed_keys:
                setattr(self, key, value)
                # exec(f"self.{key} = '{value}'")
    # def __init_subclass__(cls):
        # print('cls dict', cls.__dict__)
        # super().__init_subclass__()
        # print(f"Called __init_subclass({cls} )")
    
    
    @property
    def peak_type(self):
        '''The peak type property should be in PEAK_TYPE_OPTIONS'''
        return self._peak_type
    
    @peak_type.setter
    def peak_type(self, value: str):
        '''The peak type property should be in PEAK_TYPE_OPTIONS'''
        # TODO select value.upper() in [i.upper() for i in self.PEAK_TYPE_OPTIONS]
        if value:
            self.type_to_model_chooser(value)
            self._peak_type = value
        else:
            raise ValueError(f'The value "{value}" for "peak_type" is not in {self.PEAK_TYPE_OPTIONS}.')
    
    def type_to_model_chooser(self, value):
        model = None
        if value:
            _val_upp = value.upper()
            prefix_set = self.peak_name if hasattr(self,'peak_name') else ''
            if 'Lorentzian'.upper() in _val_upp :
                model = LorentzianModel(prefix=prefix_set)
            elif 'Gaussian'.upper() in _val_upp :
                model = GaussianModel(prefix=prefix_set)
            elif 'Voigt'.upper() in _val_upp :
                model = VoigtModel(prefix=prefix_set)
            else:
                raise NotImplementedError(f'This peak type or model "{value}" has not been implemented.')
            self.model = model

    @property
    def peak_name(self):
        '''This is the name that the peak will get as prefix'''
        return self._peak_name
    
    @peak_name.setter
    def peak_name(self, value : str, maxlen = 20):
        if len(value) < maxlen:
            prefix_set = value + '_'
            if hasattr(self,'model'):
                if self.model:
                    self.model.prefix = prefix_set
            self._peak_name = value
        else:
            raise ValueError(f'The value "{value}" for peak_name is too long({len(value)}) (max. {maxlen}).')

    @property
    def input_param_settings(self):
        '''
        this property  defines the initial parameters settings for the peak model.
        '''
        return self._input_param_settings
        # TODO maybe read in param settings form eg xls file

    @input_param_settings.setter
    def input_param_settings(self, value):
        '''
        This setter validates and converts the input parameter settings (dict) argument
        for the lmfit Parameters class.
        '''
        params = Parameters()
        try:
            _default_params = [Parameter(k, **val) for k, val in self.default_settings.items()]
            params.add_many(*_default_params)
        except Exception as e:
            raise ValueError(f'Unable to create a Parameter from default_parameters {self.default_settings}:\n{e}')

        if not isinstance(value, dict):
            raise TypeError('input_param_settings should be of type dictionary not {type(value)}')
        else:
            _valid_parlst = []
            for k,val in value.items():
                try:
                    _par = Parameter(k, **val)
                    _valid_parlst.append(_par)
                except Exception as e:
                    raise ValueError(f'Unable to create a Parameter from {k} and {val}:\n{e}')
            if _valid_parlst:
                try:

                    params.add_many(*_valid_parlst)

                except Exception as e:
                    raise ValueError(f'Unable to add many Parameters from {_valid_parlst}:\n{e}')
        self._input_param_settings = params
        self.set_model_params_hints()

    def set_model_params_hints(self):
        if issubclass(self.model.__class__, Model):
            try:
                for pname,pars in self.input_param_settings.items():
                    try:
                        self.model.set_param_hint(pname, **pars)
                    except Exception as e:
                        _error = f'Error in make_model_hints, check param_hints for {pname} with {pars}'
            except Exception as e:
                _error = f'Error in make_model_hints, check param_hints'
    @property
    def name(self):
        return self.__class__.__name__

    @classmethod
    def getfile(cls):
        return inspect.getfile(cls)

    @classmethod
    def getmodule(cls):
        return inspect.getmodule(cls)

    def __repr__(self):
        _name =  self.__class__.__name__
        _repr = f'{_name}'
        if hasattr(self, 'model'):
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
        else:
            print(f'No model set for: {self}')

def clutter():
    pass
            # elif not all(isinstance(i,dict) for i in value.values()):
        #     raise TypeError('input_param_settings should be a nested dictionary not {[type(i) i for i in value.values()])}')
        # elif not all('value' in i.keys() for i in value.values()):
        #     raise ValueError('input_param_settings should be a nested dictionary with at least a "value : .." setting not {type(value)}')
        # elif not all(k,val for k,val in i.items() for i in value.values()):
        #     param_settings = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
        #             'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
        #             'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        # return param_settings

    # @property
    # def normalization(self):
    #     ''' The normalization = True only for internal code purposes.
    #     Optional param_settings and only used to make the normalization of the spectra.
    #     '''
    #     return self._normalization
    
    # @normalization.setter
    # def normalization(self, value):
    #     ''' Check if normalization is True that the param settings are there.'''
    #     if value and not self.normalization_param_settings:
    #         raise ValueError('When normalization is set True there should be a valid parameters setting')
    #     elif value and self.normalization_param_settings:
    #         self.assign_settings_to_params()
    #     elif not value:
    #         pass
    #     else:
    #         pass
    #     self._normalization = value
    
    # # @classmethod
    # def normalization_param_settings(self):
    #     '''
    #     If the child class is used in the normalization of the spectrum then
    #     this method should be defined similar to the input_param_settings.
    #     '''
    #     return {}

    # @property
    # def gammavary(self):
    #     return self._gammavary
        
    # @normalization.setter
    # def gammavary(self, value):
    #     ''' Check if True that the settings are there'''
    #     if value and not self.gammavary_settings:
    #         raise ValueError('When gammavary is set True there should be a valid parameters setting for gamma')
    #     elif not value:
    #         self._gammavary = value
    #     else:
    #         pass
#%% TESTING

class NewChildClass(BasePeak):
    '''New child class for easier definition'''
    _test = 'testkwarg'
    
    def __init__(self,**kwargs):
        self.peak_type = 'Voigt'
        self.peak_name ='R2D2'
        
        
        self.input_param_settings = {
                            'center':
                                {'value': 2435,'min': 2400, 'max': 2550},
                            'sigma':
                                {'value': 30,'min' : 1, 'max': 200},
                            'amplitude' :
                                {'value': 2,'min' : 1E-03, 'max': 100}
                                }
        super().__init__(self)
        # print(self.__dict__)

class NoSuper(BasePeak):
    '''New child class for easier definition'''
    _test = 'testkwarg'
    
    def __init__(self):
        self.peak_name ='R2D2'
        self.peak_type = 'cartVoigt'
        
        self.input_param_settings = {
                            'center':
                                {'value': 2435,'min': 2400, 'max': 2550},
                            'sigma':
                                {'value': 30,'min' : 1, 'max': 200},
                            'amplitude' :
                                {'value': 2,'min' : 1E-03, 'max': 100}
                                }

nosup = NoSuper()
class Child(BasePeak):
    '''sss'''
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    pass
def _testing():
    
    print(filter(lambda x: x not in NewChildClass._intern+['__module__'], NewChildClass.__dict__.keys()))
    NewChildClass()
#%%
class Basetest():
    
    a = 1
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        for k,val in kwargs.items():
            setattr(self, k, val)
            
    @property
    def aprop(self):
        return self._aprop
    
    @aprop.setter
    def aprop(self, value):
        print(f'setting aprop to {value}')
        self._aprop = value




def ValidateInputParameterSettings(value):
    _allowed_keys = ['center', 'sigma', 'amplitude', 'gamma']
    
    # if not isinstance(value, dict):
    #      raise TypeError('input_param_settings should be of type dictionary not {type(value)}')
    #  else:
    #      for k,val in value.items():
    #          k,val
     
    #  elif not all(isinstance(i,dict) for i in value.values()):
    #      raise TypeError('input_param_settings should be a nested dictionary not {[type(i) i for i in value.values()])}')
    #  elif not all('value' in i.keys() for i in value.values()):
    #      raise ValueError('input_param_settings should be a nested dictionary with at least a "value : .." setting not {type(value)}')
    #  elif not all(k,val for k,val in i.items() for i in value.values()):
    #      value = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
    #              'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
    #              'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}






class tt(Basetest):
    
    a = 2
    aprop = 'tt'
    
    def __init__(self,a=a,aprop = aprop, **kwargs):
        super().__init__(a=a, aprop = aprop, **kwargs)
        
        

class t2(Basetest):
    
    a_ = 2
    aprop_ = 'tt'
    
    def __init__(self,a=a_,aprop = aprop_, **kwargs):
        super().__init__(**kwargs)
        
def _tt():
    
    b = Basetest()
    b.a
    b2 = Basetest(a=2,b=3)
    b2.a
    
    tt1 = tt()
    tt1.a
    tt2 = t2()
    tt2.aprop






    
    