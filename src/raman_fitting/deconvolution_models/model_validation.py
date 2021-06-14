#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:08:26 2021

@author: zmg
"""

# import inspect
from warnings import warn
from itertools import groupby
from collections import namedtuple

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from lmfit import Parameters

_file_parent_name = Path(__file__).parent.name
print(__name__,__file__,f'name: {_file_parent_name}')

if __name__ == '__main__': #or _file_parent_name == 'deconvolution_models':

    import first_order_peaks
    import second_order_peaks
    import normalization_peaks
    from .base_peak import BasePeak
else:
    from .base_peak import BasePeak
    from . import first_order_peaks
    from . import second_order_peaks
    from . import normalization_peaks

class NotFoundAnyModelsWarning(UserWarning):
    pass
class CanNotInitializeModelWarning(UserWarning):
    pass

#%%
class PeakModelValidator():
    '''
    This class collects all BasePeak type classes, which are costum lmfit type models, and
    constructs an iterable collection of all defined.
    '''

    _standard_modules = [first_order_peaks, second_order_peaks, normalization_peaks]
    _base_model = BasePeak

    _modvalid = namedtuple('ModelValidation', 'valid peak_group model_inst message')

    debug = False

    # standard_model_selection = []
    # _bad_models = []
    # _skip_models = []
    # endwsith = '_peak'

    def __init__(self, *args, **kwargs):
        # self.model_prefixes = model_prefixes
        # self._endswith = endwsith
        self.debug = self._set_debug(**kwargs)

        self._inspect_modules_all = []
        self._inspect_models = []
        self._inspect_models_grpby = {}
        self.find_inspect_models()

        self.valid_models = []
        self._invalid_models = []
        self.validation_inspect_models()

        # self._skipped_models = {}
        # self.selected_models = [()]
        # self.model_constructor()
        self.lmfit_models = []
        self.options = ()
        self.extra_assignments()

    def _set_debug(self, **value):
        _debug = self.debug
        if isinstance(value, dict):
            if 'debug' in value.keys():
                _debug = bool(value.get('debug', False))
        return _debug

    def find_inspect_models(self):
        _all_subclasses = self._base_model.subclasses
        self._inspect_modules_all = _all_subclasses
        # [cl for i in (inspect.getmembers(mod, inspect.isclass)
                                # for mod in self._standard_modules)
                                     # for cl in i]
        self._inspect_models = _all_subclasses
                                # [a for a in _all_subclasses
                                # if issubclass(a,self._base_model)
                                # and a is not self._base_model]
        self._inspect_models_grpby = groupby(self._inspect_models, key=lambda x:x.__module__)

        if not self._inspect_modules_all:
            warn(f'\nNo classes were found in inspected modules:\n {", ".join(self._standard_modules)}\n', NotFoundAnyModelsWarning)
        elif not self._inspect_models:
            warn(f'\nNo base models were found in:\n {", ".join([str(i) for i in self._inspect_modules_all])}.\n', NotFoundAnyModelsWarning)
        # assert self._inspect_models, 'inspect.getmembers found 0 models, change the search parameters for _standard_modules or _base_model'

    def validation_inspect_models(self):
        _model_validations = []

        for ngr,gr in  self._inspect_models_grpby:
            for m in gr:
                try:
                    _succes, _inst, _msg = self.validate_model_instance(m)
                except Exception as e:
                    _msg = f'Unexpected error for validate model instance : {e}\n'
                    _succes, _inst = False, m
                finally:
                    _args = (_succes,ngr, _inst, _msg)
                    if self.debug:
                        print(_args)


                    _model_validations.append(self._modvalid(*_args))

        self._invalid_models = [i for i in _model_validations if not i.valid]
        self.valid_models = [i for i in _model_validations if i.valid]
        self.selected_models = self.filter_valid_models(self.valid_models)
        self.selected_models = self.sort_selected_models(self.selected_models)
                    # self._invalid_models.add((False, m, _msg))
        if not self.valid_models:
            warn(f'\nNo valid models were found in:\n {", ".join([str(i) for i in self._inspect_modules_all])}\
                \t\nOnly invalid models: {", ".join([str(i) for i in self._invalid_models])}.\n', NotFoundAnyModelsWarning)

    def filter_valid_models(self, value):
        ''' Optional extra filters for valid model selection'''
        return value
        # self._skipped_models = set(self._bad_models + self._skip_models)
        # if self.standard_model_selection:
            # self.selected_models = [i for i in self.valid_models if not i.model_inst.name in self._skipped_models]
        # if self._endswith:
            # self.selected_models = [(m, ngr) for m, ngr in self.valid_models
                                    # if (i.model_inst.name.endswith(self._endswith) and not i.model_inst.name  in self._skipped_models)]
    def sort_selected_models(self, value):
        ''' Sorting the selected valid models for color assigment etc..'''
        _sorted = value
        try:
            _setting_key = [i for i in self._base_model._fields if 'param_hints' in i]
            if value:
                if _setting_key:
                    _sorted = sorted(value, key= lambda x: getattr(x.model_inst,_setting_key[0]).get('center',0))
        except Exception as e:
            raise(f'Unable to sort:\n {value}\n{e}' )
        finally:
            _sorted = sorted(_sorted, key= lambda x:x.peak_group)
            return _sorted

    def validate_model_instance(self, value):
        '''
        Returns a boolean, model and message depending on the validation of the model class.
        Invalid classes can raise warnings, but exception only when no valid models are found.
        '''

        try:
            if self.debug:
                print(f'validate model inst value:', value)
            _inst = value()
            if self.debug:
                print(f'validate model inst:', _inst)
        except Exception as e:
            _err = f'Unable to initialize model {value},\n{e}'
            warn(f'{_err}', CanNotInitializeModelWarning)
            return (False, value, _err)

        for field in self._base_model._fields:
            if not hasattr( _inst,field):
                return (False, value,'instance {_inst} has no attr {field}.\n')
            if not getattr(_inst, field):
                return (False, value,'instance {_inst}, {field} is None.\n')
            if 'param_hints' in field:
                _settings = getattr(_inst, field)
                _center = _settings.get('center', None)
                if not _center:
                    return (False, value,'instance {_inst}, settings {_settings} center is None.\n')
        return (True, _inst,f'{_inst} is a valid model')

    def extra_assignments(self):

        if self.selected_models:
            self.assign_colors_to_mod_inst()
            self.add_model_names_var_names()
        # self.add_standard_init_params()
            self.set_options()

    def assign_colors_to_mod_inst(self):
        self.cmap_set = plt.get_cmap('Dark2' if not len(self.selected_models) > 10 else 'tab20')

        for n, _arg in enumerate(self.selected_models):
            _m_inst = _arg.model_inst
            _m_inst._modelvalidation = _arg
            _m_inst.color =  ', '.join([str(i) for i in self.cmap_set(n)])
            # _m_inst._funcname = str(m).split('__main__.')[-1][:-2]
            _m_inst._lenpars = len(_m_inst.peak_model.param_names)
            self.lmfit_models.append(_m_inst)
        self.lmfit_models= sorted(self.lmfit_models, key= lambda x: x._lenpars)
        # self.lmfit_models = _mod_inst

    def add_standard_init_params(self):
        self.standard_init_params = Parameters()
        self.standard_init_params.add_many(*BasePeak._params_guesses_base)

    def add_model_names_var_names(self):
        _modvars = {i.peak_model.name : i.peak_model.param_names for i in self.lmfit_models}
        self.modpars = _modvars

    def get_df_models_parameters(self):
        _models = pd.DataFrame([(i.model.name,len(i.peak_model.param_names),', '.join(i.peak_model.param_names))
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
        _repr = 'Model Collection'
        if self.selected_models:
            _selmods = f', {len(self.selected_models)} models from: '+'\n\t- '
            _repr += _selmods
            _joinmods = '\n\t- '.join([f'{i.peak_group}: {i.model_inst} \t'
                                       for i in self.selected_models])
            _repr += _joinmods
        else:
            _repr += ', empty selected models'
        return _repr

if __name__ == '__main__':
    a = PeakModelValidator(debug=True)
