
from collections import OrderedDict

from functools import partialmethod

import inspect
from warnings import warn

# import operator
# from abc import ABC, abstractmethod
from lmfit.models import VoigtModel,LorentzianModel, GaussianModel, Model
from lmfit import Parameter,Parameters
# from lmfit import CompositeModel

class BasePeakWarning(UserWarning): # pragma: no cover
    pass

    #%%

class BasePeak(type):
    '''Base class for typical intensity peaks found the raman spectra.\
    Several peaks combined are used as a model (composed in the fit_models module)\
        to fit a certain region of the spectrum.'''

    _fields = ['peak_name','peak_type','param_hints']
    _sources = ('kwargs', 'cls_dict', 'init')
    _synonyms = {'peak_name' : [], 'peak_type' : [], 'param_hints' : ['input_param_settings']}

    PEAK_TYPE_OPTIONS = ['Lorentzian', 'Gaussian', 'Voigt']
    _PARAM_HINTS_ARGS = inspect.signature(Parameter).parameters.keys()
    # ('value', 'vary', 'min', 'max', 'expr') # optional
    default_settings = {'gamma':
                             {'value': 1,
                              'min': 1E-05,
                              'max': 70,
                              'vary': False}
                         }
    _intern = list(super.__dict__.keys())+['__module__','_kwargs']
    _fail_register = []
    # input_param_hints = {}
    _kwargs = {}

    # instances = {}
    subclasses = []

    _debug = False

    # def __call__(cls, *args, **kwargs):
    #     print(f'Request received to create an instance of class: {cls}...')
    def __prepare__(name, bases, **kwargs):

        if 'debug' in kwargs.keys():
            if kwargs.get('debug', False):

                print(f'__prepare ,name {name}, bases{bases}, kwargs {kwargs}')
        kwargs.update({'debug': False}) # FIXME check debug
        return kwargs

    def __new__(mcls, name, bases, cls_dict, **kwargs):
        if 'debug' in kwargs.keys() or cls_dict.keys():
            if kwargs.get('debug', False) or cls_dict.get('debug', False):
                mcls._debug = True
                print(f"Called __new ({mcls} ),name {name}, bases{bases}, cls_dict {cls_dict.keys()} kwargs {kwargs}")
        # print(f'vars: {vars(cls)}')

        # Init the fco which check and stores the values for each field
        # when fco.status == True then the green light for class initialization is given
        fco = FieldsCoordinator(fields= mcls._fields, sources = mcls._sources )

        # First thing add input from source kwargs to fco
        fco.multi_store('kwargs', **kwargs)
        # kwargs_ = {k : val for k,val in cls_dict.items() if k in cls_object._fields}
        _cls_dict_field_kwargs = {}
        # Second thing, check class dict for field values,
        # store and replace field values with properties from metaclass
        for field in mcls._fields:
            if field in cls_dict.keys():# delete field from cls_dict and store in fco
                value = cls_dict[field]
                fco.store('cls_dict', field, value)
                _cls_dict_field_kwargs.update({field: value})
                del cls_dict[field]
            if hasattr(mcls, field): # store new field property in cls dict
                _obj = getattr(mcls, field)
                if isinstance(_obj, property): # if mcls has property function with name == field
                    cls_dict[field] = _obj # stores property in cls_dict before init so it will be set as a property for cls instance

        # Fourth: replace init with newly defined function
        def init_(self, *args, **kwargs):
            # print(f'child __init__ mod called {self}, {kwargs}')
                # super()
            if hasattr(self, 'fco'):
                for k,val in self.fco.results.items():
                    setattr(self, k, val['value'])
                    # print(f'child __init__ setattr called {k}, {val}')

        # Third thing, check class __init__ for setting of field valuesm and delete from cls dict
        if '__init__' in cls_dict.keys():
            cls_init_part_obj = partialmethod(cls_dict['__init__'])

            sig = inspect.signature(cls_dict['__init__'])
            # breakpoint()
            _cls_init_part_obj_funcs = {k: val for k, val in cls_dict.items()
                                        if inspect.isfunction(val) and k != '__init__'}

            for fname, func in _cls_init_part_obj_funcs.items():
                setattr(cls_init_part_obj,fname, func)
                cls_init_part_obj_dct_keys = set(cls_init_part_obj.__dict__.keys())
                sig = inspect.signature(func)
                try:
                    func(cls_init_part_obj)
                except Exception as e:
                    warn(f'Definition of the __init__ {fname} fails, please redefine init in class, \n{e}', BasePeakWarning)

            # breakpoint()
            try:
                cls_init_part_obj.func(cls_init_part_obj)
            except AttributeError:
                warn(f'Definition of the __init__ {name} fails, please redefine {fco.missing} in class', BasePeakWarning)
            _cls_init_part_fco_dict = mcls._cleanup_init_dict(cls_init_part_obj.__dict__)
            fco.multi_store('init', **_cls_init_part_fco_dict)


            del cls_dict['__init__']
        else:
            cls_dict['__init__'] = init_

        if fco.status:
            pass
            # print(f'Good class definition all values for fields are present: {fco.results}', BasePeakWarning)
        else:
            warn(f'Definition for {name} is not complete, please redefine {fco.missing} in class', BasePeakWarning)

        cls_object = super().__new__(mcls, name, bases, cls_dict) #,*args, **{**_attrs_found, **kwargs})

        setattr(cls_object,'__init__', init_)
        setattr(cls_object,'_fields', mcls._fields)
        setattr(cls_object,'fco', fco)

        setattr(cls_object,'PEAK_TYPE_OPTIONS', mcls.PEAK_TYPE_OPTIONS)
        setattr(cls_object,'_PARAM_HINTS_ARGS', mcls._PARAM_HINTS_ARGS)


        # print(f'__new cls obj new init set: {cls_object.__init__}')
        # print(f'__new cls dict init set: {cls_dict.get("__init__", None)}')
        cls_object = mcls._set_other_methods(cls_object)
        # print(f'__new__ instance {cls_object} end,\n {dir(cls_object)}')
        return cls_object

    def __init__(self, name, bases, cls_dict, *args, **kwargs):
        # print(f"__init_ base called ({self} with args {args} and kwargs {kwargs})")
        # subclassess are appended here
        if self not in self.subclasses:
            self.subclasses.append(self)
        super().__init__(name, bases, cls_dict, *args, **kwargs)
        # print(f"__init_ super called ({self.__init__})")

    @classmethod
    def _cleanup_init_dict(cls, _dict):
        _dkeys = list(_dict.keys())
        _result = {}
        while _dkeys:
            _dk = _dkeys.pop()
            _kmatch = [(i, _dk) for i in cls._synonyms.keys() if i in _dk] # clean field match
            _synmatch = [(k, syn) for k,val in cls._synonyms.items() for syn in val if syn in _dk] # synonym field match
            # print(_dk, _kmatch,_synmatch)
            if _kmatch:
                _result.update({i[0] : _dict[i[1]] for i in _kmatch})
            elif not _kmatch and _synmatch:
                _result.update({i[0] : _dict[i[1]] for i in _synmatch})
        return _result

    @classmethod
    def _set_other_methods(cls, cls_object):
        _other_methods = [i for i in dir(cls)
                          if not i.startswith('_')
                          and not i == 'mro']
                          # and not hasattr(cls_object, i)]
        for method in _other_methods:
            # print(f'__new setting method {method}')
            _mcls_obj = getattr(cls, method)
            if method.endswith('__'):
                method = f'__{method}'

            if not isinstance(_mcls_obj, property):
                    setattr(cls_object, method, _mcls_obj)
            # if callable(_mcls_obj):
                # pass
                # print(f'__new setting {method} {_mcls_obj} is callable')
                # print(f'__new setting {method} {_mcls_obj} is NOT callable')
            # try:
            #     # print(f'__new setting {method} with {_get}')
            #     pass
            #         # print(f'__new setting method SUCCES {method}, {_mcls_obj}')
            # except AttributeError as e:
            #     cls._fail_register.append((method, e))
            #     # print(f'__new setting method FAILED {method}, {e}')
            # except TypeError as e:
            #     cls._fail_register.append((method, e))
            #     # print(f'__new setting method FAILED TypeError {method}, {e}')
        return cls_object

    @property
    def peak_type(self):
        '''The peak type property should be in PEAK_TYPE_OPTIONS'''
        return self._peak_type

    @peak_type.setter
    def peak_type(self, value: str):
        '''The peak type property should be in PEAK_TYPE_OPTIONS'''
        if any([value.upper() == i.upper() for i in self.PEAK_TYPE_OPTIONS]):
            # self.type_to_model_chooser(value)
            self._peak_type = value
        elif any([i.upper() in value.upper() for i in self.PEAK_TYPE_OPTIONS]):
            _opts = [i for i in self.PEAK_TYPE_OPTIONS if i.upper() in value.upper()]
            if len(_opts) == 1:
                value_ = _opts[0]
                self._peak_type = value_
                warn(f'Peak type misspelling mistake check {value}, forgiven and fixed with {value_}', BasePeakWarning)
            elif len(_opts) > 1:
                raise ValueError(f'Multiple options {_opts} for misspelled value "{value}" in {self.PEAK_TYPE_OPTIONS}.')
            else:
                raise ValueError(f'Multiple options {_opts} for misspelled value "{value}" in {self.PEAK_TYPE_OPTIONS}.')
        else:
            raise ValueError(f'The value "{value}" for "peak_type" is not in {self.PEAK_TYPE_OPTIONS}.')

    @property
    def peak_model(self):
        '''The peak model property is constructed from peak name and param hints'''
        # if hasattr(self, '_peak_model'):
        return self._peak_model

    @peak_model.setter
    def peak_model(self,value):
        '''The peak model property is constructed from peak name and param hints'''

        if issubclass(value.__class__, Model):# or value == None:
            self._peak_model = value
        else:
            raise TypeError(f'Value {value} {type(value)} is not of type lmfit.Model or None')

    @property
    def param_hints(self):
        '''The params_hints property is constructed param hints'''
        # if hasattr(self, '_peak_model'):
        return self._param_hints

    @param_hints.setter
    def param_hints(self,value):
        '''The peak model property is constructed from peak name and param hints'''
        param_hints_ = self.param_hints_constructor(value)
        # print(f'== inside params hints {self}, {value}, {param_hints_}')
        model = self.call_make_model_from_params(param_hints_)
        self.peak_model = model
        self._param_hints = param_hints_

    # @classmethod
    def call_make_model_from_params(self, param_hints_):
        prefix_= self.peak_name if hasattr(self,'peak_name') else ''
        peak_type_ = self.peak_type if hasattr(self,'peak_type') else ''
        model = self.make_model_and_set_param_hints(prefix_, peak_type_, param_hints_)
        return model

    # @classmethod
    def make_model_and_set_param_hints(self, prefix_, peak_type_, param_hints_):
        try:
            # prefix_set = self.peak_name if hasattr(self,'peak_name') else ''
            # breakpoint()
            model = self.type_to_model_chooser(peak_type_, prefix_)
            model = self.set_model_params_hints(model, param_hints_)
            model._metadata= (self.__class__, prefix_, peak_type_, param_hints_)
            # model = self.model_set_param_hints_delegator(model)
            return model
        except Exception as e:
            warn(f'make model and set param hints failed \n {e}', BasePeakWarning)
            return None

    # @classmethod
    def type_to_model_chooser(self, value, prefix_):
        model = None
        if value:
            _val_upp = value.upper()
            if 'Lorentzian'.upper() in _val_upp :
                model = LorentzianModel(prefix=prefix_)
            elif 'Gaussian'.upper() in _val_upp :
                model = GaussianModel(prefix=prefix_)
            elif 'Voigt'.upper() in _val_upp :
                model = VoigtModel(prefix=prefix_)
            else:
                raise NotImplementedError(f'This peak type or model "{value}" has not been implemented.')
            # if model and hasattr(self, '_input_param_hints'):
                # model = self.set_model_params_hints(model, self.input_param_hints)
        return model

    @property
    def peak_name(self):
        '''This is the name that the peak Model will get as prefix'''
        return self._peak_name

    @peak_name.setter
    def peak_name(self, value : str, maxlen = 20):
        '''This is the name that the peak will get as prefix'''
        if len(value) < maxlen:
            prefix_set = value + '_'
            if hasattr(self,'peak_model'):
                try:
                    self.peak_model.prefix = prefix_set
                except Exception as e:
                    warn(f'Peak name can not be set as prefix on model \n{e}', BasePeakWarning)
            self._peak_name = value
        else:
            raise ValueError(f'The value "{value}" for peak_name is too long({len(value)}) (max. {maxlen}).')

    def param_hints_constructor(self, value):
        '''
        This setter validates and converts the input parameter settings (dict) argument
        for the lmfit Parameters class.
        '''
        params = Parameters()

        if hasattr(self,'default_settings'):
            try:
                _default_params = [Parameter(k, **val) for k, val in self.default_settings.items()]
                params.add_many(*_default_params)
            except Exception as e:
                raise ValueError(f'Unable to create a Parameter from default_parameters {self.default_settings}:\n{e}')

        if not isinstance(value, dict):
            raise TypeError(f'input_param_hints should be of type dictionary not {type(value)}')

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
        return params

    def set_model_params_hints(self, model, param_hints_):
        _error = ''
        if issubclass(model.__class__, Model) and issubclass(param_hints_.__class__,Parameters):
            try:
                for pname,par in param_hints_.items():
                    try:
                        _par_hint_dict = {pn:  getattr(par,pn, None)
                                          for pn in self._PARAM_HINTS_ARGS if getattr(par,pn, None)}
                        # _par_hint_dict = {k: val for k, val in _par_hint_dict.items() if val}
                        model.set_param_hint(**_par_hint_dict)
                    except Exception as e:
                        _error += f'Error in make_model_hints, check param_hints for {pname} with {par}, {e}'
                # return model
            except Exception as e:
                _error += f'Error in make_model_hints, check param_hints \n{e}'
        else:
            _error += f'TypeError in make_model_hints, check {param_hints_} or {model}'
        if _error:
            warn('Errors found in setting of param hints: {_error}', BasePeakWarning)
        return model

    def repr__(self):
        _repr = f'{self.__class__.__name__}'
        if hasattr(self, 'peak_model'):
            _repr += f', {self.peak_model}'
            _param_center = ''
            if self.peak_model:
                _param_center = self.peak_model.param_hints.get('center', {})
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
        if self.peak_model:
            self.peak_model.print_param_hints()
        else:
            print(f'No model set for: {self}')
#%%

class FieldsCoordinatorWarning(UserWarning):
    pass

class FieldsCoordinator:
    '''
    Keeps check of the fields from multiple sources,
    allows to store values in dict
    yields results a single results from several sources for each field
    status is True when all fields in results have at least one value
    '''

    def __init__(self, fields: list = [], sources: tuple = [], **kwargs):
        self.fields = fields
        self.sources = sources
        self._register_template = self.make_register(sources, fields)
        self.set_sources_attr()
        self._results = {}


    def make_register(self, sources, fields):
        _reg = {source: {field : None for field in fields} for source in sources }
        return _reg

    def set_sources_attr(self):
        for source in self.sources:
            setattr(self,f'{source}', self._register_template[source])

    @property
    def register(self):
        _reg = {source: getattr(self, source) for source in self.sources }
        return _reg

    @property
    def status(self):
        _st = False
        if set(self.results) == set(self.fields):
            _st = True
        return _st

    @property
    def results(self):
        return self._results

    def _set_results(self):
        _results = self.get_values_from_all_fields()
        self._results = _results


    @property
    def missing(self):
        results= self.results
        _missing = set(self.fields) - set(results.keys())
        return _missing

    def get_values_from_all_fields(self):
        _result_values = {}
        for field in self.fields:
            _fvaldict_sources = self.get_field_value_from_sources(field)
            if _fvaldict_sources:
                _src = {'source' : i for i in _fvaldict_sources.keys()}
                _value = {'value' : i for i in _fvaldict_sources.values()}
                _nice_result = {**_src, **_value}
                _result_values.update({field: _nice_result})
        return _result_values

    def get_field_value_from_sources(self, field):
        _fsvals = OrderedDict({})
        _result = {}
        for source in self.sources:
            _src = getattr(self, source)
            _fval = _src.get(field, None)
            if _fval:
                _fsvals.update({source : _fval})
        if not dict in map(type,_fsvals.values()):
            _setvals = set(_fsvals.values())
        else:
            _setvals = _fsvals.values()
        _setsources = set(_fsvals.keys())
        _lstsources = list(_setsources)
        if len(_setvals) == 1:
            _fval = list(_setvals)[0]
            if len(_setsources ) == 1:
                _src = _lstsources[0]
            elif len(_setsources ) > 1:
                _src = list(_fsvals.keys())[0]
                warn(f'Field {field} has multiple sources {_setsources}, one value ', FieldsCoordinatorWarning)
            _result =  {_src: _fval}
        elif len(_setvals) > 1:
            # breakpoint()
            _firstval = list(_fsvals.items())[0]
            warn(f'Field {field} has multiple sources {_setsources}, different values follow order of sources ', FieldsCoordinatorWarning)
            _result =  {_firstval[0] : _firstval[1]}
        return _result

    def multi_store(self, source: str, **kwargs):
        # _fields_dict = {k: val for k, val in _dict.items() if k in self.fields}
        _fields_kwargs = {k: val for k, val in kwargs.items() if k in self.fields}
        # _input_dict = {**_fields_kwargs, **_fields_dict}
        if _fields_kwargs :
            for field, val in _fields_kwargs.items():
                self.store(source, field, val)
            self._set_results()

    def store(self, source, field, val):
        if source in self.sources and field in self.fields and val:
            _src = getattr(self,source)
            _fval = _src.get(field, None)
            if not _fval:
                _src[field] = val
            elif _fval == val:
                warn(f'Redefinition of {field} in {source} ignored', FieldsCoordinatorWarning)
            elif _fval != val:
                _src[field] = val
                warn(f'Overwriting of {field} in {source} with new value! {_fval} is not {val}', FieldsCoordinatorWarning)
            else:
                warn(f'Store {source} {val} unexpected', FieldsCoordinatorWarning)

            setattr(self,source, _src)
            self._set_results()
        else:
            warn(f'Store in {source} at {field} not in {self.sources} or not in {self.fields} or not {val}, ignored.', FieldsCoordinatorWarning)
            pass # store values not recognized

    #%%
