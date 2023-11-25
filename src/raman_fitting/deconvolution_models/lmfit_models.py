from ast import main
import inspect
from functools import partialmethod
import math

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

LMFIT_PARAM_KWARGS = ("value", "vary", "min", "max", "expr")


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

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    name: str
    value: Optional[float]
    vary: Optional[bool] = True
    min: Optional[float] = Field(-math.inf, allow_inf_nan=True)
    max: Optional[float] = Field(math.inf, allow_inf_nan=True)
    expr: Optional[str] = None
    parameter: Optional[Parameter] = Field(None, exclude=True)

    @model_validator(mode="after")
    def check_min_max(self) -> "LMFitParameterHints":
        min, max = self.min, self.max
        if min is not None and max is not None and min > max:
            raise ValueError("Min must be less than max")
        return self

    @model_validator(mode="after")
    def check_value_min_max(self) -> "LMFitParameterHints":
        value, min, max = self.value, self.min, self.max
        if value is not None:
            if min is not None and value < min:
                raise ValueError("Value must be greater than min")
            if max is not None and value > max:
                raise ValueError("Value must be less than max")
        return self

    @model_validator(mode="after")
    def check_construct_parameter(self) -> "LMFitParameterHints":
        if self.parameter is None:
            self.parameter = Parameter(
                name=self.name,
                value=self.value,
                vary=self.vary,
                min=self.min,
                max=self.max,
                expr=self.expr,
            )
        return self


DEFAULT_GAMMA_PARAM_HINT = LMFitParameterHints(
    name="gamma", value=1, min=1e-05, max=70, vary=False
)

LMFIT_MODEL_MAPPER = {
    "Lorentzian": LorentzianModel,
    "Gaussian": GaussianModel,
    "Voigt": VoigtModel,
}


def parmeter_to_dict(parameter: Parameter) -> dict:
    ret = {k: getattr(parameter, k) for k in LMFIT_PARAM_KWARGS}
    ret = {k: v for k, v in ret.items() if v is not None}
    return ret


def main():
    breakpoint()


if __name__ == "__main__":
    main()
