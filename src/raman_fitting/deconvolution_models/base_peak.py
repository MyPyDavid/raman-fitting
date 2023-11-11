import inspect
from functools import partialmethod

from os import name
from pyexpat import model

from unittest.mock import DEFAULT
from warnings import warn
from enum import StrEnum

from lmfit import Parameter, Parameters

from lmfit.models import GaussianModel, LorentzianModel, Model, VoigtModel

from typing import List, Literal, Optional, Dict, final
import numpy

from pydantic import (
    BaseModel,
    ConfigDict,
    InstanceOf,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pytest import param


param_hint_dict = Dict[str, Dict[str, Optional[float | bool | str]]]


class BasePeakWarning(UserWarning):  # pragma: no cover
    pass


PEAK_TYPE_OPTIONS = StrEnum("PEAK_TYPE_OPTIONS", ["Lorentzian", "Gaussian", "Voigt"])


class LMFitParameterHints(BaseModel):
    """
    https://github.com/lmfit/lmfit-py/blob/master/lmfit/model.py#L566

    The given hint can include optional bounds and constraints
    ``(value, vary, min, max, expr)``, which will be used by
    `Model.make_params()` when building default parameters.

    While this can be used to set initial values, `Model.make_params` or
    the function `create_params` should be preferred for creating
    parameters with initial values.

    The intended use here is to control how a Model should create
    parameters, such as setting bounds that are required by the mathematics
    of the model (for example, that a peak width cannot be negative), or to
    define common constrained parameters.

    Parameters
    ----------
    name : str
        Parameter name, can include the models `prefix` or not.
    **kwargs : optional
        Arbitrary keyword arguments, needs to be a Parameter attribute.
        Can be any of the following:

        - value : float, optional
            Numerical Parameter value.
        - vary : bool, optional
            Whether the Parameter is varied during a fit (default is
            True).
        - min : float, optional
            Lower bound for value (default is ``-numpy.inf``, no lower
            bound).
        - max : float, optional
            Upper bound for value (default is ``numpy.inf``, no upper
            bound).
        - expr : str, optional
            Mathematical expression used to constrain the value during
            the fit.

    Example
    --------
    >>> model = GaussianModel()
    >>> model.set_param_hint('sigma', min=0)

    """

    name: str
    value: Optional[float]
    vary: Optional[bool] = True
    min: Optional[float] = numpy.inf * -1
    max: Optional[float] = numpy.inf
    expr: Optional[str] = None


DEFAULT_GAMMA_PARAM_HINT = LMFitParameterHints(
    name="gamma", value=1, min=1e-05, max=70, vary=False
)

LMFIT_MODEL_MAPPER = {
    "Lorentzian": LorentzianModel,
    "Gaussian": GaussianModel,
    "Voigt": VoigtModel,
}


class BasePeak(BaseModel):
    """
    --------
    Example usage
    --------
    Base class for easier definition of typical intensity peaks found in the
    raman spectra.

    The go al of is this metaclass is to be able to more easily write
    peak class definitions (for possible user input). It tries to find three
    fields in the definition, which are requiredfor a LMfit model creation,
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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    peak_name: str
    param_hints: Optional[
        Parameters | List[LMFitParameterHints] | param_hint_dict
    ] = None
    peak_type: Optional[str] = None
    is_substrate: Optional[bool] = False
    normalization_peak: Optional[bool] = False
    docstring: Optional[str] = Field(None, repr=False)
    lmfit_model: Optional[InstanceOf[Model]] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lmfit_model = self.create_peak_model()

    @field_validator("param_hints")
    @classmethod
    def check_param_hints(
        cls, v: Optional[Parameters | List[LMFitParameterHints] | param_hint_dict]
    ) -> Optional[Parameters]:
        if v is None:
            return v
        if isinstance(v, Parameters):
            return v

        if isinstance(v, dict):
            valid_p_hints = [LMFitParameterHints(name=k, **val) for k, val in v.items()]

        if isinstance(v, list):
            assert all(isinstance(i, LMFitParameterHints) for i in v)

        pars_hints = [Parameter(**i.model_dump()) for i in valid_p_hints]
        params = Parameters()
        params.add_many(*pars_hints)
        return params

    @model_validator(mode="after")
    def check_lmfit_model(self) -> "BasePeak":
        if self.lmfit_model is not None:
            if isinstance(self.lmfit_model, Model):
                return self
            else:
                raise ValueError(
                    f"lmfit_model is not a Model instance, but {type(self.lmfit_model)}"
                )
        peak_type = self.peak_type
        peak_name = self.peak_name
        param_hints = self.param_hints
        if peak_type is None:
            raise ValueError("peak_type is None")

        lmfit_model = self.create_peak_model()
        if lmfit_model is None:
            raise ValueError("lmfit_model is None")
        for k, v in lmfit_model.param_hints.items():
            lmfit_model.set_param_hint(k, **v)

        self.lmfit_model = lmfit_model

        return self

    def create_peak_model(self):
        """returns the lmfit model instance according to the chosen peak type and sets the prefix from peak_name"""
        model = None
        if self.peak_name:
            # breakpoint()
            capitalized = self.peak_type.capitalize()
            try:
                lmfit_model_class = LMFIT_MODEL_MAPPER[capitalized]
                model = lmfit_model_class(prefix=self.peak_name_prefix)
            except IndexError:
                raise NotImplementedError(
                    f'This peak type or model "{self.peak_type}" has not been implemented.'
                )
        return model

    @property
    def peak_name_prefix(self):
        if not self.peak_name:
            return ""
        if self.peak_name.endswith("_"):
            return self.peak_name
        return self.peak_name + "_"

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


class _OldBasePeak(type):
    """ """

    _fields = ["peak_name", "peak_type", "param_hints"]
    _sources = ("user_input", "kwargs", "cls_dict", "init", "class_name")
    _synonyms = {
        "peak_name": [],
        "peak_type": [],
        "param_hints": ["input_param_settings"],
    }

    PEAK_TYPE_OPTIONS = PEAK_TYPE_OPTIONS

    # ('value', 'vary', 'min', 'max', 'expr') # optional
    default_settings = {"gamma": {"value": 1, "min": 1e-05, "max": 70, "vary": False}}

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

                    _peak_model = create_peak_model_from_name_type_param_hints(
                        **create_model_kwargs
                    )
                    self.create_model_kwargs = create_model_kwargs
                except Exception as e:
                    print(f"try make models:\n{self}, \n\t {e}")
            else:
                pass
        else:
            pass
            print(f"missing field {self.fco.missing} {self},\n")
        return _peak_model

    def print_params(self):
        if self.peak_model:
            self.peak_model.print_param_hints()
        else:
            print(f"No model set for: {self}")


PARAMETER_ARGS = inspect.signature(Parameter).parameters.keys()


def create_peak_model_from_name_type_param_hints(
    peak_model: Model = None,
    peak_name: str = None,
    peak_type: str = None,
    param_hints: Parameters = None,
):
    if peak_model:
        param_hints = peak_model.make_params()
        peak_name_ = peak_model.prefix
        peak_type_ = peak_model.func.__name__
        if peak_name:
            if peak_name != peak_name_:
                raise Warning("changed name of peak model")
        else:
            peak_name = peak_name_
        if peak_type:
            if peak_type != peak_type_:
                raise Warning("changed type of peak model")
                peak_model = make_model_from_peak_type_and_name(
                    peak_name=peak_name, peak_type=peak_type
                )
        if param_hints:
            if param_hints != param_hints:
                peak_model = set_params_hints_on_model(peak_model, param_hints)
        else:
            peak_model = set_params_hints_on_model(peak_model, param_hints)
    else:
        if peak_name:
            pass
        else:
            raise Warning(
                "no peak_name given for create_peak_model, peak_name will be default"
            )
        if peak_type:
            peak_model = make_model_from_peak_type_and_name(
                peak_name=peak_name, peak_type=peak_type
            )
            if param_hints:
                peak_model = set_params_hints_on_model(peak_model, param_hints)
    return peak_model


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

    try:
        params_list = [Parameter(k, **val) for k, val in param_hints.items()]
        params.add_many(*params_list)
    except Exception as exc:
        raise ValueError(
            f"Unable to create a Parameter from {param_hints}:\n{exc}"
        ) from exc

    return params


def set_params_hints_on_model(model, param_hints):
    _error = ""
    if isinstance(model, Model) and isinstance(param_hints, Parameters):
        try:
            for pname, par in param_hints.items():
                try:
                    _par_hint_dict = {
                        pn: getattr(par, pn, None)
                        for pn in PARAMETER_ARGS
                        if getattr(par, pn, None)
                    }
                    model.set_param_hint(**_par_hint_dict)
                except Exception as e:
                    _error += f"Error in make_model_hints, check param_hints for {pname} with {par}, {e}"
        except Exception as e:
            _error += f"Error in make_model_hints, check param_hints \n{e}"
    else:
        _error += f"TypeError in make_model_hints, check types of model {type(model)} param_hints{type(param_hints)}"
    if _error:
        warn("Errors found in setting of param hints: {_error}", BasePeakWarning)
    return model


def _main():
    print(settings["first_order"]["models"])
    peaks = {}
    peak_items = {
        **settings["first_order"]["peaks"],
        **settings["second_order"]["peaks"],
    }.items()
    for k, v in peak_items:
        peaks.update({k: BasePeak(**v)})

    D_peak = BasePeak(**settings["first_order"]["peaks"]["D"])
    model_items = {
        **settings["first_order"]["models"],
        **settings["second_order"]["models"],
    }.items()
    models = {}
    for model_name, model_comp in model_items:
        print(k, v)
        comps = model_comp.split("+")
        peak_comps = [peaks[i] for i in comps]
        lmfit_comp_model = sum(
            map(lambda x: x.lmfit_model, peak_comps), peak_comps.pop().lmfit_model
        )
        models[model_name] = lmfit_comp_model
        print(lmfit_comp_model)
    breakpoint()


if __name__ == "__main__":
    _main()
