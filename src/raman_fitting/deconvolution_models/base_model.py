""" The member of the validated collection of BasePeaks are here assembled into fitting Models"""

import logging
from warnings import warn

from lmfit import Model

from .. import __package_name__

logger = logging.getLogger(__package_name__)


_SUBSTRATE_PEAK = "Si1_peak"

if __name__ == "__main__":
    from peak_validation import PeakModelValidator
else:
    from .peak_validation import PeakModelValidator

#%%

# ====== InitializeMode======= #
class InitializeModels:
    """
    This class will initialize and validate the different fitting models.
    The models are of type lmfit.model.CompositeModel and stored in a dict with names
    for the models as keys.
    """

    _standard_1st_order_models = {
        "2peaks": "G+D",
        "3peaks": "G+D+D3",
        "4peaks": "G+D+D3+D4",
        "5peaks": "G+D+D2+D3+D4",
        "6peaks": "G+D+D2+D3+D4+D5",
    }
    _standard_2nd_order_models = {"2nd_4peaks": "D4D4+D1D1+GD1+D2D2"}

    def __init__(self, standard_models=True):
        self._cqnm = self.__class__.__name__

        self.peak_collection = self.get_peak_collection(PeakModelValidator)

        self.all_models = {}
        self.construct_standard_models()
        # self.normalization_model = self.peak_collection.normalization

    def get_peak_collection(self, func):
        try:
            peak_collection = func()
            logger.debug(
                f"{self._cqnm} collection of peaks validated with {func}:\n{peak_collection}"
            )

        except Exception as e:
            logger.error(f"{self._cqnm} failure in call {func}.\n\t{e}")
            peak_collection = []
        return peak_collection

    def construct_standard_models(self):

        _models = {}
        _models_1st = {
            f"1st_{key}": BaseModel(
                peak_collection=self.peak_collection, model_name=value
            )
            for key, value in self._standard_1st_order_models.items()
        }
        _models.update(_models_1st)
        _models_1st_no_substrate = {
            f"1st_{key}": BaseModel(
                peak_collection=self.peak_collection, model_name=value
            )
            for key, value in self._standard_1st_order_models.items()
        }
        _models.update(_models_1st_no_substrate)
        self.first_order = {**_models_1st, **_models_1st_no_substrate}

        _models_2nd = {
            key: BaseModel(peak_collection=self.peak_collection, model_name=value)
            for key, value in self._standard_2nd_order_models.items()
        }
        _models.update(_models_2nd)
        self.second_order = _models_2nd
        self.all_models = _models

    def __repr__(self):
        _t = "\n".join(map(str, self.all_models.values()))
        return _t


class BaseModelWarning(UserWarning):
    pass


class BaseModel:
    """
    This Model class combines the collection of valid peaks from BasePeak into a regression model of type lmfit.model.CompositeModel
    that is compatible with the lmfit Model and fit functions.
    The model_name, include_substrate and lmfit_model attributes are kept consistent w.r.t. their meaning when they are set.

    Parameters
    --------
        model_name: string ==> is converted to lmfit Model object
        include_substrate: bool ==> toggle between True and False to include a substrate peak

    """

    _SEP = "+"
    _SUFFIX = "_"

    # TODO change include substrate to  has substrate and remove from init
    def __init__(
        self,
        model_name: str = "",
        peak_collection=PeakModelValidator(),
        substrate_peak_name: str = _SUBSTRATE_PEAK,
    ):

        self.peak_collection = peak_collection
        self.peak_options = self.set_peak_options()
        self.substrate_peak_name = substrate_peak_name
        # self.include_substrate = include_substrate
        # has_substrate: bool = False,
        self._substrate_name = self.substrate_peak_name.split(self._SUFFIX)[0]
        self.model_name = model_name

        self.lmfit_model = self.model_constructor_from_model_name(self.model_name)
        # self.model_constructor()
        # self.peak_dict = self.peak_collection.get_dict()

    def set_peak_options(self):
        _opts = {}
        for _pk in self.peak_collection.options:
            try:
                _prefix = _pk.split(self._SUFFIX)[0]
                if _prefix:
                    _opts.update({_prefix: _pk})
            except Exception as e:
                warn(
                    f'Peak {_pk} not valid name "{self._SUFFIX}, error:\n{e}',
                    BaseModelWarning,
                )
        return _opts

    @property
    def model_name(self):
        return self._model_name

    @model_name.setter
    def model_name(self, name):
        """Model name for str => model conversion"""
        _ch = True
        name = self.validate_model_name_input(name)
        if hasattr(self, "_model_name"):
            if name == self._model_name:
                _ch = False
        if _ch:
            self.lmfit_model = self.model_constructor_from_model_name(name)
            # self._equalize_name_choice(name)
            self._model_name = name

    @property
    def has_substrate(self):
        _has = False
        if hasattr(self, "model_name"):
            _has = self.name_contains_substrate(self.model_name)

        return _has

    @has_substrate.setter
    def has_substrate(self, value):
        # _hasattr_model = hasattr(self, 'model')
        raise AttributeError(
            f'{self.__class__.__name__} this property can not be set "{value}", use add_ or remove_ substrate function.'
        )
        # _ch = True
        # if hasattr(self,'_include_substrate'):
        #     if _choice == self._include_substrate:
        #         _ch = False
        # if _ch:
        #     self._equalize_name_choice(None, _choice)
        #     self._include_substrate = _choice
        # self._include_substrate = _choice

    def name_contains_substrate(self, _name):
        """Checks if name contains the substrate name, returns bool"""
        _name_contains_any = False
        if type(_name) == str:
            _name_contains_any = any(
                i == self._substrate_name for i in _name.split("+")
            )
        return _name_contains_any

    def remove_substrate(self):
        if hasattr(self, "model_name"):
            _name = self.model_name
            if self.name_contains_substrate(_name):
                warn(
                    f'\n{self.__class__.__name__} remove substrate is called so "{self._substrate_name}" is removed from {_name}.\n',
                    BaseModelWarning,
                )
                _new_name = "+".join(
                    i for i in _name.split("+") if i not in self._substrate_name
                )  # remove substr name
                if _new_name != _name:
                    self.model_name = _new_name
        # return _name

    def add_substrate(self):
        if hasattr(self, "model_name"):
            _name = self.model_name
            if not self.name_contains_substrate(_name):
                _new_name = _name + f"+{self._substrate_name}"  # add substr name
                if _new_name != _name:
                    self.model_name = _new_name
        # return _name

    def validate_model_name_input(self, value):
        """checks if given input name is valid"""
        if not type(value) == str:
            raise TypeError(
                f'Given name "{value}" for model_name should be a string insteady of type({type(value).__name__})'
            )
        elif not value:
            warn(f'\n\tThis name "{value}" is an empty string', BaseModelWarning)
            return value
        elif not "+" in value:
            warn(
                f'\n\tThis name "{value}" does not contain the separator "+". (could be just 1 Peak)',
                BaseModelWarning,
            )
            return value
        else:
            _clean_string = "".join([i for i in value if i.isalnum() or i == "+"])
            _splitname = _clean_string.split("+")
            if not _splitname or not any(bool(i) for i in _splitname):
                raise ValueError(f'The split with sep "+" of name {value} is empty')
            else:
                return "+".join([i for i in _splitname if i])

    def model_constructor_from_model_name(self, _name):
        """Construct a lmfit.Model from the string model name"""

        _discarded_terms = []
        _peak_names = []
        if _name:
            for _peak in _name.split(self._SEP):  # filter model name for last time
                _peak_from_opts = self.peak_options.get(_peak, None)
                if _peak_from_opts:
                    _peak_names.append(_peak_from_opts)
                else:
                    _discarded_terms.append(_peak)

        _peak_models = [
            self.peak_collection.model_dict.get(i) for i in _peak_names if i
        ]
        if _discarded_terms:
            warn(
                f'Model evalution for "{_name}" discarded terms {",".join(_discarded_terms)} => clean: {_peak_names}',
                BaseModelWarning,
            )

        if not _peak_models:
            _lmfit_model = None
        elif len(_peak_models) == 1:
            _lmfit_model = _peak_models[0].peak_model
        elif len(_peak_models) >= 2:
            # _eval_model_name = ' + '.join([i[0] for i in _peak_models])
            _composite_model = None
            for _pkmod in _peak_models:
                _mod = _pkmod.peak_model
                if not _composite_model:
                    _composite_model = _mod
                else:
                    try:
                        _composite_model += _mod
                    except Exception as e:
                        warn(
                            f"Model add operation failed for constructing Composite Model {_pkmod.name}.\n {e}",
                            BaseModelWarning,
                        )
            _lmfit_model = _composite_model

        if not issubclass(type(_lmfit_model), Model):
            warn(
                f"Model constructor does not yield type ({type(Model)} {type(_lmfit_model)}.",
                BaseModelWarning,
            )
        return _lmfit_model

    def __repr__(self):

        _choice = "no" if not self.has_substrate else "yes"
        _txt = f"{self.model_name}, substrate ({_choice}): "
        if hasattr(self, "lmfit_model"):
            _txt += "\n\t" + repr(self.lmfit_model)
        else:
            _txt += "empty model"
        return _txt

    # def _0equalize_from_model_name(self,_name):
    #     pass
    # def _0equalize_from_incl_substrate(self,_choice):
    #     pass
    # def _0equalize_name_choice(self, _name, _choice):
    #     _change = False
    #     if _choice != None and _name == None and hasattr(self, '_model_name'):
    #         # change model name when choice is set
    #         _name = self._add_or_rem_substrate_to_model_name(_choice, self._model_name)
    #         if _name != self._model_name:
    #             _change = True
    #             self._model_name = _name
    #     if _name != None and _choice == None and hasattr(self, '_include_substrate'):
    #         # change include subtrate choice when model name is set
    #         _name_contains = self._name_contains_substrate(_name)
    #         if _name_contains != self._include_substrate:
    #             _change = True
    #             self._include_substrate = _name_contains
    #         if hasattr(self,'_model_name'):
    #             _change = bool(_name != self._model_name)
    #     # if _name != None and hasattr(self, '_model_name')
    #     print(f'Change {_change}, name {_name}, choice {_choice}')
    #     if _change  and _name:
    #         self.lmfit_model = self.model_constructor_from_model_name(_name)
    #     elif not _choice and _contains:
    #         _substr_name = self.substrate_peak_name.split(self._SUFFIX)[0]
    #         warn(f'\n{self.__class__.__name__} include substrate is set to {_choice} so "{_substr_name}" is removed from {_name}.\n',BaseModelWarning)
    #         _name = '+'.join(i for i in _name.split('+') if i not in _substr_name)  # remove substr name

    # def _0add_or_rem_substrate_to_model_name(self, _choice, _name):
    #     _substr_name = self.substrate_peak_name.split(self._SUFFIX)[0]
    #     _contains = self._name_contains_substrate(_name)
    #     if _choice and not _contains:
    #         _name = _name+f'+{_substr_name}'  # add substr name
    #     elif not _choice and _contains:
    #         warn(f'\n{self.__class__.__name__} include substrate is set to {_choice} so "{_substr_name}" is removed from {_name}.\n',BaseModelWarning)
    #         _name = '+'.join(i for i in _name.split('+') if i not in _substr_name)  # remove substr name
    #     return _name
