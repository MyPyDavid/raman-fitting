import logging
from warnings import warn

from lmfit import Model

from .peak_validation import PeakModelValidator
from .base_model import BaseModel

logger = logging.getLogger(__name__)


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

