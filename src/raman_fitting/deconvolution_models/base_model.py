""" The members of the validated collection of BasePeaks are assembled here into fitting Models"""
import logging
from warnings import warn

from lmfit import Model

from raman_fitting.deconvolution_models.peak_validation import PeakModelValidator

logger = logging.getLogger(__name__)

_SUBSTRATE_PEAK = "Si1_peak"


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

    # IDEA change include substrate to  has substrate and remove from init
    def __init__(
        self,
        model_name: str = "",
        peak_collection=PeakModelValidator(),
        substrate_peak_name: str = _SUBSTRATE_PEAK,
    ):
        self.peak_collection = peak_collection
        self.peak_options = self.set_peak_options()
        self.substrate_peak_name = substrate_peak_name
        self._substrate_name = self.substrate_peak_name.split(self._SUFFIX)[0]
        self.model_name = model_name
        self.lmfit_model = self.model_constructor_from_model_name(self.model_name)

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
            self._model_name = name

    @property
    def has_substrate(self):
        _has = False
        if hasattr(self, "model_name"):
            _has = self.name_contains_substrate(self.model_name)

        return _has

    @has_substrate.setter
    def has_substrate(self, value):
        raise AttributeError(
            f'{self.__class__.__name__} this property can not be set "{value}", use add_ or remove_ substrate function.'
        )

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

    def add_substrate(self):
        if hasattr(self, "model_name"):
            _name = self.model_name
            if not self.name_contains_substrate(_name):
                _new_name = _name + f"+{self._substrate_name}"  # add substr name
                if _new_name != _name:
                    self.model_name = _new_name

    def validate_model_name_input(self, value):
        """checks if given input name is valid"""
        if type(value) != str:
            raise TypeError(
                f'Given name "{value}" for model_name should be a string insteady of type({type(value).__name__})'
            )
        elif not value:
            warn(f'\n\tThis name "{value}" is an empty string', BaseModelWarning)
            return value
        elif "+" not in value:
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
