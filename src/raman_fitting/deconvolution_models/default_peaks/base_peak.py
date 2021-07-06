# from collections import OrderedDict

import inspect
from functools import partialmethod
from keyword import iskeyword as _iskeyword
from warnings import warn

from lmfit import Parameter, Parameters

# import operator
# from abc import ABC, abstractmethod
from lmfit.models import GaussianModel, LorentzianModel, Model, VoigtModel

# from lmfit import CompositeModel

# print('name: ',__name__,'file: ', __file__, __package__)

if __name__ in ("__main__"):  #'base_peak'
    from raman_fitting.utils.coordinators import FieldsTracker as FieldsTracker
else:
    from ...utils.coordinators import FieldsTracker

# __all__ = [Base]


#%%
class BasePeakWarning(UserWarning):  # pragma: no cover
    pass


class BasePeak(type):
    """
    Base class for easier definition of typical intensity peaks found in the
    raman spectra.

    The goal of is this metaclass is to be able to more easily write
    peak class definitions (for possible user input). It tries to find three
    fields in the definition, which are required for a LMfit model creation,
    namely: peak_name, peak_type and the param hints.

    peak_name:
        arbitrary name as prefix for the peak
    peak_type:
        defines the lineshape of the peak, the following options are implemented:
        "Lorentzian", "Gaussian", "Voigt"
    params_hints:
        initial values for the parameters of the peak, at least
        a value for the center position of the peak should be given.

    It tries to find these fields in different sources such as: the class definition
    with only class attributes, init attributes or even in the keywords arguments.
    The FieldsTracker class instance (fco) keeps track of the definition in different
    sources and can check when all are ready. If there are multiple sources with definitions
    for the same field than the source with highest priority will be chosen (based on tuple order).
    Each field is a propery which validates the assigments.

    Sort of wrapper for lmfit.model definition.
    Several of these peaks combined are used to make the lmfit CompositeModel
    (composed in the fit_models module), which will be used for the fit.

    --------
    Example usage
    --------

    "Example class definition with attribute definitions"
    class New_peak(metaclass=BasePeak):
        "New peak child class for easier definition"

        param_hints = { 'center': {'value': 2435,'min': 2400, 'max': 2550}}
        peak_type = 'Voigt' #'Voigt'
        peak_name ='R2D2'

    New_peak().peak_model == <lmfit.Model: Model(voigt, prefix='R2D2_')>

    "Example class definition with keyword arguments"

    New_peak = BasePeak('new',
                        peak_name='D1',
                        peak_type= 'Lorentzian',
                        param_hints = { 'center': {'value': 1500}}
    )
    New_peak()


    """

    _fields = ["peak_name", "peak_type", "param_hints"]
    _sources = ("user_input", "kwargs", "cls_dict", "init", "class_name")
    _synonyms = {
        "peak_name": [],
        "peak_type": [],
        "param_hints": ["input_param_settings"],
    }

    PEAK_TYPE_OPTIONS = ["Lorentzian", "Gaussian", "Voigt"]

    # ('value', 'vary', 'min', 'max', 'expr') # optional
    default_settings = {"gamma": {"value": 1, "min": 1e-05, "max": 70, "vary": False}}
    # _intern = list(super.__dict__.keys())+['__module__','_kwargs']
    subclasses = []

    _debug = False

    # def __call__(cls, *args, **kwargs):
    #     print(f'Request received to create an instance of class: {cls}...')
    def __prepare__(name, bases, **kwargs):
        """prepare method only for debugging"""
        if "debug" in kwargs.keys():
            if kwargs.get("debug", False):
                print(f"__prepare ,name {name}, bases{bases}, kwargs {kwargs}")
        # kwargs.update({'debug': False})
        return kwargs

    def __new__(mcls, name, *args, **kwargs):

        # print(
        #             f"Called __new ,_args {_}"
        #         )
        if len(args) == 2:
            # default arg __new__ input
            bases, cls_dict = args
        else:
            bases, cls_dict = (), {}

        if kwargs.get("debug", False):
            mcls._debug = True
        if cls_dict.get("debug", False):
            mcls._debug = True
        if mcls._debug:
            print(
                f"Called __new ({mcls} ),name {name}, bases{bases}, cls_dict {cls_dict.keys()} kwargs {kwargs}"
            )
        # print(f'vars: {vars(cls)}')

        # From namdedtuple source:
        # test input arguments names
        for name_ in [name] + list(kwargs.keys()):
            if type(name_) is not str:
                raise TypeError("Class name and keywords names must be strings")
            if not name_.isidentifier():
                raise ValueError(
                    "Class name and keywords names must be valid "
                    f"identifiers: {name_!r}"
                )
            if _iskeyword(name_):
                raise ValueError(
                    "Class name and keywords names cannot be a " f"keyword: {name_!r}"
                )

        # Init the fco which check and stores the values for each field
        # when fco.status == True then the green light for class initialization is given
        fco = FieldsTracker(fields=mcls._fields, sources=mcls._sources)

        # First thing add input from source kwargs to fco
        fco.multi_store("kwargs", **kwargs)

        # Also add input class name to fco
        fco.multi_store("class_name", **{"peak_name": name})
        # kwargs_ = {k : val for k,val in cls_dict.items() if k in cls_object._fields}
        _cls_dict_field_kwargs = {}
        # Second thing, check class dict for field values,
        # store and replace field values with properties from metaclass
        for field in mcls._fields:
            if field in cls_dict.keys():  # delete field from cls_dict and store in fco
                value = cls_dict[field]
                fco.store("cls_dict", field, value)
                _cls_dict_field_kwargs.update({field: value})
                del cls_dict[field]
            if hasattr(mcls, field):  # store new field property in cls dict
                _obj = getattr(mcls, field)
                if isinstance(
                    _obj, property
                ):  # if mcls has property function with name == field
                    cls_dict[
                        field
                    ] = _obj  # stores property in cls_dict before init so it will be set as a property for cls instance

        # Third: Define the 'new' init for the class, which sets the values from the fco results
        def _init_subclass_replacement(self, *args, **kwargs):
            if self._debug:
                print(f"child __init__ mod called {self}, {kwargs}")
            # super()
            if hasattr(self, "fco"):
                for k, val in self.fco.results.items():
                    setattr(self, k, val["value"])
                    if self._debug:
                        print(f"fco child __init__ setattr called {k}, {val}")

            # if hasattr(self, 'peak_model'):
            setattr(self, "create_peak_model", self.create_peak_model)
            setattr(self, "peak_model", self.create_peak_model())

        # Fourth thing, check class __init__ for setting of field values and delete from cls dict
        if "__init__" in cls_dict.keys():
            cls_init_part_obj = partialmethod(cls_dict["__init__"])

            sig = inspect.signature(cls_dict["__init__"])
            # breakpoint()
            _cls_init_part_obj_funcs = {
                k: val
                for k, val in cls_dict.items()
                if inspect.isfunction(val) and k != "__init__"
            }

            for fname, func in _cls_init_part_obj_funcs.items():
                setattr(cls_init_part_obj, fname, func)
                cls_init_part_obj_dct_keys = set(cls_init_part_obj.__dict__.keys())
                sig = inspect.signature(func)
                try:
                    func(cls_init_part_obj)
                except Exception as e:
                    warn(
                        f"Definition of the __init__ {fname} fails, please redefine init in class, \n{e}",
                        BasePeakWarning,
                    )
            try:
                cls_init_part_obj.func(cls_init_part_obj)
            except AttributeError:
                warn(
                    f"Definition of the __init__ {name} fails, please redefine {fco.missing} in class",
                    BasePeakWarning,
                )
            _cls_init_part_fco_dict = mcls._cleanup_init_dict(
                cls_init_part_obj.__dict__
            )
            fco.multi_store("init", **_cls_init_part_fco_dict)

            cls_dict["_original_init_"] = cls_dict["__init__"]

            del cls_dict["__init__"]
        else:
            pass

        cls_dict["__init__"] = _init_subclass_replacement

        if fco.status:
            pass
            # print(f'Good class definition all values for fields are present: {fco.results}', BasePeakWarning)
        else:
            warn(
                f"Definition for {name} is not complete, please redefine {fco.missing} in class",
                BasePeakWarning,
            )

        if mcls._debug:
            print(
                f"Calling super__new__() ({mcls} ),name {name}, bases{bases}, cls_dict {cls_dict.keys()}"
            )
        cls_object = super().__new__(
            mcls, name, bases, cls_dict
        )  # ,*args, **{**_attrs_found, **kwargs})
        if mcls._debug:
            print(f"Called super__new__() ({mcls} ),cls_object: {cls_object}")
        # setattr(cls_object, "__init__", init_)
        setattr(cls_object, "_fields", mcls._fields)
        setattr(cls_object, "_debug", mcls._debug)
        setattr(cls_object, "fco", fco)
        setattr(cls_object, "PEAK_TYPE_OPTIONS", mcls.PEAK_TYPE_OPTIONS)
        cls_object = mcls._set_other_methods(cls_object)
        return cls_object

    def __init__(self, name, *args, **kwargs):
        # bases, cls_dict removed and kept only *args
        # print(f"__init_ base called ({self} with name '{name}' args {args} and kwargs {kwargs})")
        # subclassess are appended here
        if self not in self.subclasses:
            self.subclasses.append(self)
        # super().__init__(name)
        # print(f"__init_ super called ({self.__init__})")

    @classmethod
    def _cleanup_init_dict(cls, _dict):
        """cleans up the __init__ dictionary from defined class"""
        _dkeys = list(_dict.keys())
        _result = {}
        while _dkeys:
            _dk = _dkeys.pop()
            _kmatch = [
                (i, _dk) for i in cls._synonyms.keys() if i in _dk
            ]  # clean field match
            _synmatch = [
                (k, syn)
                for k, val in cls._synonyms.items()
                for syn in val
                if syn in _dk
            ]  # synonym field match
            # print(_dk, _kmatch,_synmatch)
            if _kmatch:
                _result.update({i[0]: _dict[i[1]] for i in _kmatch})
            elif not _kmatch and _synmatch:
                _result.update({i[0]: _dict[i[1]] for i in _synmatch})
        return _result

    @classmethod
    def _set_other_methods(cls, cls_object):
        """sets other methods found in this baseclass on the defined cls object"""
        _other_methods = [
            i for i in dir(cls) if not i.startswith("_") and not i == "mro"
        ]
        # and not hasattr(cls_object, i)]
        for method in _other_methods:
            # print(f'__new setting method {method}')
            _mcls_obj = getattr(cls, method)
            if method.endswith("__") and not method.startswith("__"):
                method = f"__{method}"

            if not isinstance(_mcls_obj, property):
                # print(f'__new setting {method} on {_mcls_obj} is callable')
                setattr(cls_object, method, _mcls_obj)
        return cls_object

    @property
    def peak_type(self):
        """This property (str) should be assigned and in self.PEAK_TYPE_OPTIONS"""
        return self._peak_type

    @peak_type.setter
    def peak_type(self, value: str):
        """The peak type property should be in PEAK_TYPE_OPTIONS"""
        if not isinstance(value, str):
            raise TypeError(f'The value "{value}" is not a string.')
        value_ = None
        if any([value.upper() == i.upper() for i in self.PEAK_TYPE_OPTIONS]):
            # self.type_to_model_chooser(value)
            value_ = value
        elif any([i.upper() in value.upper() for i in self.PEAK_TYPE_OPTIONS]):
            _opts = [i for i in self.PEAK_TYPE_OPTIONS if i.upper() in value.upper()]
            if len(_opts) == 1:
                value_ = _opts[0]

                warn(
                    f"Peak type misspelling mistake check {value}, forgiven and fixed with {value_}",
                    BasePeakWarning,
                )
            elif len(_opts) > 1:
                raise ValueError(
                    f'Multiple options {_opts} for misspelled value "{value}" in {self.PEAK_TYPE_OPTIONS}.'
                )
            else:
                raise ValueError(
                    f'Multiple options {_opts} for misspelled value "{value}" in {self.PEAK_TYPE_OPTIONS}.'
                )
        else:
            raise ValueError(
                f'The value "{value}" for "peak_type" is not in {self.PEAK_TYPE_OPTIONS}.'
            )
        if value_:
            self._peak_type = value_
            self.fco.store("user_input", "peak_type", value)
            # self.set_peak_model_from_fields()
            self.peak_model = self.create_peak_model()

    @property
    def peak_model(self):
        if not hasattr(self, "_peak_model"):
            self.create_peak_model()
        else:
            return self._peak_model

    @peak_model.setter
    def peak_model(self, value):
        """
        This property is an instance of lmfit.Model,
        constructed from peak_type, peak_name and param_hints setters
        """
        if not isinstance(value, Model):
            self._peak_model = self.create_peak_model()
        else:
            self._peak_model = value

    def create_peak_model(self):
        _peak_model = None
        if self.fco.status:
            if all(hasattr(self, field) for field in self._fields):

                try:
                    create_model_kwargs = dict(
                        peak_name=self.peak_name,
                        peak_type=self.peak_type,
                        param_hints=self.param_hints,
                    )

                    if hasattr(self, "create_model_kwargs"):
                        _orig_kwargs = self.create_model_kwargs

                    _peak_model = LMfitModelConstructorMethods.create_peak_model_from_name_type_param_hints(
                        **create_model_kwargs
                    )
                    self.create_model_kwargs = create_model_kwargs
                    # model = self.make_model_and_set_param_hints(prefix_, peak_type_, param_hints_)
                except Exception as e:
                    print(f"try make models:\n{self}, \n\t {e}")
            else:
                pass
        else:
            pass
            print(f"missing field {self.fco.missing} {self},\n")
        return _peak_model

    @property
    def param_hints(self):
        """This property is dict of dicts and sets the initial values for the parameters"""
        # if hasattr(self, '_peak_model'):
        if hasattr(self, "_param_hints"):
            if isinstance(self._param_hints, Parameters):
                return self._param_hints
            else:
                raise TypeError(
                    f"{self.__class__.__name__} self._param_hints is not instance of Parameters"
                )

    @param_hints.setter
    def param_hints(self, value, **kwargs):
        # print(f'paramhints: val:{value},\nkw:{kwargs}')
        if isinstance(value, Parameters):
            param_hints_ = value
        else:
            dict_ = {}
            if isinstance(value, dict):
                dict_ = {**dict_, **value}
            if kwargs:
                dict_ = {**dict_, **kwargs}
            # print(f'paramhints: {self},\n {dict_}')
            param_hints_ = LMfitModelConstructorMethods.param_hints_constructor(
                param_hints=dict_, default_settings=self.default_settings
            )
        self._param_hints = param_hints_
        self.fco.store("user_input", "param_hints", param_hints_)
        if not isinstance(self, BasePeak):
            self.peak_model = self.create_peak_model()

    @property
    def peak_name(self):
        """This is the name that the peak_model will get as prefix"""
        if self._peak_name:
            if not self._peak_name.endswith("_"):
                self._peak_name = self._peak_name + "_"
        return self._peak_name

    @peak_name.setter
    def peak_name(self, value: str, maxlen=20):
        if len(value) < maxlen:
            prefix_set = value + "_"
            self._peak_name = value
            # print(f"peak_name set:{value}")
            self.fco.store("user_input", "peak_name", value)
            self.peak_model = self.create_peak_model()
            # self.set_peak_model_from_fields()
        else:
            raise ValueError(
                f'The value "{value}" for peak_name is too long({len(value)}) (max. {maxlen}).'
            )

    def repr__(self):
        _repr = f"{self.__class__.__name__}"
        if hasattr(self, "peak_model"):
            _repr += f", {self.peak_model}"
            _param_center = ""
            if self.peak_model:
                _param_center = self.peak_model.param_hints.get("center", {})
            if _param_center:
                _center_txt = ""
                _center_val = _param_center.get("value")
                _center_min = _param_center.get("min", _center_val)
                if _center_min != _center_val:
                    _center_txt += f"{_center_min} < "
                _center_txt += f"{_center_val}"
                _center_max = _param_center.get("max", _center_val)
                if _center_max != _center_val:
                    _center_txt += f" > {_center_max}"
                _repr += f", center : {_center_txt}"
        else:
            _repr += ": no Model set"
        return _repr

    def print_params(self):
        if self.peak_model:
            self.peak_model.print_param_hints()
        else:
            print(f"No model set for: {self}")


#%%

#%%
# LMfitModelConstructorMethods.create_peak_model_from_name_type_param_hints(peak_model= new.peak_model)
# new.peak_name
#%%
class LMfitModelConstructorMethods:

    PARAMETER_ARGS = inspect.signature(Parameter).parameters.keys()

    @classmethod
    def create_peak_model_from_name_type_param_hints(
        cls,
        peak_model: Model = None,
        peak_name: str = None,
        peak_type: str = None,
        param_hints: Parameter = None,
    ):
        if peak_model:
            param_hints_ = peak_model.make_params()
            peak_name_ = peak_model.prefix
            peak_type_ = peak_model.func.__name__
            if peak_name:
                if peak_name != peak_name_:
                    raise Warning("changed name of peak model")
                    peak_model.prefix = peak_name
            else:
                peak_name = peak_name_
            if peak_type:
                if peak_type != peak_type_:
                    raise Warning("changed type of peak model")
                    peak_model = cls.make_model_from_peak_type_and_name(
                        peak_name=peak_name, peak_type=peak_type
                    )
            if param_hints:
                if param_hints != param_hints_:
                    peak_model = cls.set_params_hints_on_model(peak_model, param_hints)
            else:
                peak_model = cls.set_params_hints_on_model(peak_model, param_hints_)
        else:
            if peak_name:
                pass
            else:
                raise Warning(
                    "no peak_name given for create_peak_model, peak_name will be default"
                )
            if peak_type:
                peak_model = cls.make_model_from_peak_type_and_name(
                    peak_name=peak_name, peak_type=peak_type
                )
                if param_hints:
                    peak_model = cls.set_params_hints_on_model(peak_model, param_hints)
        return peak_model

    def make_model_from_peak_type_and_name(peak_type="Lorentzian", peak_name=""):
        """returns the lmfit model instance according to the chosen peak type and sets the prefix from peak_name"""
        model = None
        if peak_type:
            _val_upp = peak_type.upper()
            if "Lorentzian".upper() in _val_upp:
                model = LorentzianModel(prefix=peak_name)
            elif "Gaussian".upper() in _val_upp:
                model = GaussianModel(prefix=peak_name)
            elif "Voigt".upper() in _val_upp:
                model = VoigtModel(prefix=peak_name)
            else:
                raise NotImplementedError(
                    f'This peak type or model "{peak_type}" has not been implemented.'
                )
        return model

    def param_hints_constructor(param_hints: dict = {}, default_settings: dict = {}):
        """
        This method validates and converts the input parameter settings (dict) argument
        into a lmfit Parameters class instance.
        """
        params = Parameters()

        if default_settings:
            try:
                _default_params = [
                    Parameter(k, **val) for k, val in default_settings.items()
                ]
                params.add_many(*_default_params)
            except Exception as e:
                raise ValueError(
                    f"Unable to create a Parameter from default_parameters {default_settings}:\n{e}"
                )
        if not isinstance(param_hints, dict):
            raise TypeError(
                f"input_param_hints should be of type dictionary not {type(param_hints)}"
            )
        else:
            _valid_parlst = []
            for k, val in param_hints.items():
                try:
                    _par = Parameter(k, **val)
                    _valid_parlst.append(_par)
                except Exception as e:
                    raise ValueError(
                        f"Unable to create a Parameter from {k} and {val}:\n{e}"
                    )
            if _valid_parlst:
                try:
                    params.add_many(*_valid_parlst)
                except Exception as e:
                    raise ValueError(
                        f"Unable to add many Parameters from {_valid_parlst}:\n{e}"
                    )
        return params

    @classmethod
    def set_params_hints_on_model(cls, model, param_hints_):
        _error = ""
        if issubclass(model.__class__, Model) and issubclass(
            param_hints_.__class__, Parameters
        ):
            try:
                for pname, par in param_hints_.items():
                    try:
                        _par_hint_dict = {
                            pn: getattr(par, pn, None)
                            for pn in cls.PARAMETER_ARGS
                            if getattr(par, pn, None)
                        }
                        # _par_hint_dict = {k: val for k, val in _par_hint_dict.items() if val}
                        model.set_param_hint(**_par_hint_dict)
                    except Exception as e:
                        _error += f"Error in make_model_hints, check param_hints for {pname} with {par}, {e}"
                # return model
            except Exception as e:
                _error += f"Error in make_model_hints, check param_hints \n{e}"
        else:
            _error += f"TypeError in make_model_hints, check types of model {type(model)} param_hints_{type(param_hints_)}"
        if _error:
            warn("Errors found in setting of param hints: {_error}", BasePeakWarning)
        return model


#%%
