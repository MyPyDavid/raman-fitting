#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:08:26 2021

@author: zmg
"""

import inspect
import logging
from collections import namedtuple
from itertools import groupby
from pathlib import Path
from typing import Tuple
from warnings import warn

import matplotlib.pyplot as plt
import pandas as pd
from lmfit import Parameters

# _file_parent_name = Path(__file__).parent.name
# print(__name__,__file__,f'name: {_file_parent_name}')

if __name__ == "__main__":  # or _file_parent_name == 'deconvolution_models':
    # import first_order_peaks
    # import second_order_peaks
    # import normalization_peaks
    from default_peaks import BasePeak
else:
    from .. import __package_name__
    from .default_peaks.base_peak import BasePeak

    logger = logging.getLogger(__package_name__)


#%%
class PeakValidationWarning(UserWarning):
    pass


class NotFoundAnyModelsWarning(PeakValidationWarning):
    pass


class CanNotInitializeModelWarning(PeakValidationWarning):
    pass


class PeakModelValidator:
    """
    This class collects all BasePeak (=BASE_PEAK) type classes, which are costum lmfit type models, and
    constructs an iterable collection of all defined Child class.
    Each subclass of BasePeak is:
        - validated: instance check
        - filtered: optional
        - sorted: sorting for valid models based on defined center position of BasePeak

    Followed by color assignment to each BasePeak and collection of lmfit_models

    """

    # _standard_modules = [first_order_peaks, second_order_peaks, normalization_peaks]
    BASE_PEAK = BasePeak

    ModelValidation = namedtuple(
        "ModelValidation", "valid peak_group model_inst message"
    )

    CMAP_OPTIONS_DEFAULT = ("Dark2", "tab20")
    fallback_color = (0.4, 0.4, 0.4, 1.0)

    debug = False

    # standard_model_selection = []
    # _bad_models = []
    # _skip_models = []
    # endwsith = '_peak'

    def __init__(self, *args, cmap_options=CMAP_OPTIONS_DEFAULT, **kwargs):
        # self.model_prefixes = model_prefixes
        # self._endswith = endwsith
        self.debug = self._set_debug(**kwargs)
        self._cmap_options = cmap_options

        self._inspect_models = self.get_subclasses_from_base(self.BASE_PEAK)

        self.valid_models = []
        self._invalid_models = []
        self.valid_models, self._invalid_models = self.validation_inspect_models(
            inspect_models=self._inspect_models
        )
        self.selected_models = self.filter_valid_models(self.valid_models)
        self.selected_models = self.sort_selected_models(self.selected_models)

        self.lmfit_models = self.assign_colors_to_lmfit_mod_inst(self.selected_models)
        self.add_model_names_var_names(self.lmfit_models)

        self.model_dict = self.get_model_dict(self.lmfit_models)
        self.options = self.model_dict.keys()

        # self.options = ()
        # self.extra_assignments()

    def _set_debug(self, **value):
        _debug = self.debug
        if isinstance(value, dict):
            if "debug" in value.keys():
                _debug = bool(value.get("debug", False))
        return _debug

    def get_subclasses_from_base(self, _BaseClass):
        """Finds subclasses of the BasePeak metaclass, these should give already valid models"""

        _all_subclasses = []
        if inspect.isclass(_BaseClass):
            if hasattr(_BaseClass, "subclasses"):
                _all_subclasses = _BaseClass.subclasses
            elif hasattr(_BaseClass, "__subclassess__"):
                _all_subclasses = _BaseClass.__subclasses__
            else:
                warn(
                    f"\nNo baseclasses were found for {str(_BaseClass)}:\n missing attributes",
                    NotFoundAnyModelsWarning,
                )
        else:
            warn(
                f"\nNo baseclasses were found for {str(_BaseClass)}:\n is not a class",
                NotFoundAnyModelsWarning,
            )

        if not _all_subclasses:
            warn(
                f"\nNo baseclasses were found in inspected modules for {str(_BaseClass)}:\n",
                NotFoundAnyModelsWarning,
            )

        return _all_subclasses

        # {", ".join(self._standard_modules)}
        # elif not self._inspect_models:
        # warn(f'\nNo base models were found in:\n {", ".join([str(i) for i in self._inspect_modules_all])}.\n', NotFoundAnyModelsWarning)
        # assert self._inspect_models, 'inspect.getmembers found 0 models, change the search parameters for _standard_modules or BASE_PEAK'

    def _inspect_modules_for_classes(self):
        """Optional method Inspect other modules for subclasses"""
        pass
        # self._inspect_modules_all = _all_subclasses
        # [cl for i in (inspect.getmembers(mod, inspect.isclass)
        # for mod in self._standard_modules)
        # for cl in i]

    def validation_inspect_models(self, inspect_models: list = []):
        """Validates each member of a list for making a valid model instance"""
        _model_validations = []
        valid_models = []

        for model in inspect_models:
            _module = model.__module__
            try:
                _succes, _inst, _msg = self.validate_model_instance(model)
            except Exception as e:
                _succes, _inst = False, model
                _msg = f"Unexpected error for validate model instance : {e}\n"
            finally:
                _args = (_succes, _module, _inst, _msg)
                _model_validations.append(self.ModelValidation(*_args))
                if self.debug:
                    print(_args)

        _invalid_models = [i for i in _model_validations if not i.valid]
        valid_models = [i for i in _model_validations if i.valid]

        if not valid_models:
            warn(
                f'\nNo valid models were found in:\n {", ".join([str(i) for i in inspect_models])}\
                \t\nOnly invalid models: {", ".join([str(i) for i in _invalid_models])}.\n',
                NotFoundAnyModelsWarning,
            )

        return valid_models, _invalid_models

    def filter_valid_models(self, value):
        """Optional method for extra filters on valid model selection"""
        return value
        # self._skipped_models = set(self._bad_models + self._skip_models)
        # if self.standard_model_selection:
        # self.selected_models = [i for i in self.valid_models if not i.model_inst.name in self._skipped_models]
        # if self._endswith:
        # self.selected_models = [(m, ngr) for m, ngr in self.valid_models
        # if (i.model_inst.name.endswith(self._endswith) and not i.model_inst.name  in self._skipped_models)]

    def sort_selected_models(self, value):
        """Sorting the selected valid models for color assigment etc.."""
        _sorted = value
        _setting_key = None
        try:
            _setting_key = [i for i in self.BASE_PEAK._fields if "param_hints" in i]
            if value:
                if _setting_key:
                    _sorted = sorted(
                        value,
                        key=lambda x: getattr(x.model_inst, _setting_key[0]).get(
                            "center", 0
                        ),
                    )
        except Exception as e:
            raise (f"Unable to sort:\n {value}\n{e}")
        finally:
            _sorted = sorted(_sorted, key=lambda x: x.peak_group)
            return _sorted

    def validate_model_instance(self, value):
        """
        Returns a boolean, model and message depending on the validation of the model class.
        Invalid classes can raise warnings, but exception only when no valid models are found.
        """

        try:
            if self.debug:
                print(f"validate model inst value:", value)
            _inst = value()
            if self.debug:
                print(f"validate model inst:", _inst)
        except Exception as e:
            _err = f"Unable to initialize model {value},\n{e}"
            warn(f"{_err}", CanNotInitializeModelWarning)
            return (False, value, _err)

        for field in self.BASE_PEAK._fields:
            if not hasattr(_inst, field):
                return (False, value, f"instance {_inst} has no attr {field}.\n")
            if not getattr(_inst, field):
                return (False, value, f"instance {_inst}, {field} is None.\n")
            if "param_hints" in field:
                _settings = getattr(_inst, field)
                _center = _settings.get("center", None)
                if not _center:
                    return (
                        False,
                        value,
                        f"instance {_inst}, settings {_settings} center is None.\n",
                    )
        return (True, _inst, f"{_inst} is a valid model")

    @staticmethod
    def get_cmap_list(
        lst, cmap_options: Tuple = (), fallback_color: Tuple = ()
    ) -> Tuple:

        cmap = [(0, 0, 0, 1) for i in lst]  # black as fallback default color

        # set fallback color from class
        if isinstance(fallback_color, tuple):
            if len(fallback_color) == 4:
                cmap = [fallback_color for i in lst]

        # set cmap colors from cmap options
        if cmap_options:

            try:
                pltcmaps = [plt.get_cmap(cmap) for cmap in cmap_options]
                # Take shortest colormap but not
                cmap = min(
                    [i for i in pltcmaps if len(lst) <= len(i.colors)],
                    key=lambda x: len(x.colors),
                    default=cmap,
                )
                # if succesfull
                if "ListedColormap" in str(type(cmap)):
                    cmap = cmap.colors

            except Exception as exc:
                logger.warning(f"get_cmap_list error setting cmap colors:{exc}")

        return cmap

    def assign_colors_to_lmfit_mod_inst(self, selected_models: list):
        cmap_get = self.get_cmap_list(
            selected_models,
            cmap_options=self._cmap_options,
            fallback_color=self.fallback_color,
        )
        lmfit_models = []
        for n, _arg in enumerate(selected_models):
            _m_inst = _arg.model_inst
            _m_inst._modelvalidation = _arg
            _m_inst.color = ", ".join([str(i) for i in cmap_get[n]])
            # _m_inst._funcname = str(m).split('__main__.')[-1][:-2]
            _m_inst._lenpars = len(_m_inst.peak_model.param_names)
            lmfit_models.append(_m_inst)
        return lmfit_models
        # self.lmfit_models= sorted(self.lmfit_models, key= lambda x: x._lenpars)
        # self.lmfit_models = _mod_inst

    def add_standard_init_params(self):
        self.standard_init_params = Parameters()
        self.standard_init_params.add_many(*BasePeak._params_guesses_base)

    def add_model_names_var_names(self, lmfit_models):
        _mod_param_names = {
            i.peak_model.name: i.peak_model.param_names for i in lmfit_models
        }
        return _mod_param_names

    def get_df_models_parameters(self):
        _models = pd.DataFrame(
            [
                (
                    i.model.name,
                    len(i.peak_model.param_names),
                    ", ".join(i.peak_model.param_names),
                )
                for i in self.lmfit_models
            ],
            columns=["Model_EEC", "model_lenpars", "model_parnames"],
        )
        return _models

    def get_model_dict(self, lmfit_models):
        model_dict = {i.__class__.__name__: i for i in lmfit_models}
        return model_dict

    def get_dict(self):
        return {
            i.__module__ + ", " + i.__class__.__name__: i for i in self.lmfit_models
        }

    def __getattr__(self, name):
        # raise AttributeError(f'Chosen name "{name}" not in in options: "{", ".join(self.options)}".')
        try:
            _options = self.__getattribute__("options")
            if name in _options:
                return self.model_dict.get(name, None)
            raise AttributeError(
                f'Chosen name "{name}" not in options: "{", ".join(_options)}".'
            )
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
        _repr = "Validated Peak model collection"
        if self.selected_models:
            _selmods = f", {len(self.selected_models)} models from: " + "\n\t- "
            _repr += _selmods
            _joinmods = "\n\t- ".join(
                [f"{i.peak_group}: {i.model_inst} \t" for i in self.selected_models]
            )
            _repr += _joinmods
        else:
            _repr += ", empty selected models"
        return _repr


if __name__ == "__main__":
    a = PeakModelValidator(debug=True)
