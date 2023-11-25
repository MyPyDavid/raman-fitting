""" The members of the validated collection of BasePeaks are assembled here into fitting Models"""
import logging

from warnings import warn
from typing import List, Optional, Dict

from lmfit.models import Model, GaussianModel

from raman_fitting.deconvolution_models.peak_validation import PeakModelValidator
from .base_peak import BasePeak, get_default_peaks

from pydantic import (
    BaseModel,
    PositiveInt,
    Field,
    ConfigDict,
    model_validator,
    ValidationInfo,
    field_validator,
    ValidationError,
)

logger = logging.getLogger(__name__)

SUBSTRATE_PEAK = "Si1_peak"
SEP = "+"
SUFFIX = "_"


class BaseModelWarning(UserWarning):
    pass


def construct_lmfit_model_from_base_peaks(base_peaks: List[BasePeak]) -> Model:
    """
    Construct the lmfit model from a collection of (known) peaks
    """
    if not base_peaks:
        raise ValueError("No peaks given to construct lmfit model from.")
    lmfit_composite_model = sum(
        map(lambda x: x.lmfit_model, base_peaks), base_peaks.pop().lmfit_model
    )
    return lmfit_composite_model


class BaseModelCollection(BaseModel):
    """
    This Model class combines the collection of valid peaks from BasePeak into a regression model
    of type lmfit.model.CompositeModel
    that is compatible with the lmfit Model and fit functions.
    The model_name, include_substrate and lmfit_model attributes are kept
    consistent w.r.t. their meaning when they are set.

    Parameters
    --------
        verbose_name: string ==> is converted to lmfit Model object
        include_substrate: bool ==> toggle between True and False to include a substrate peak

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    peaks: str
    default_peaks: Dict[str, BasePeak] = Field(
        default_factory=get_default_peaks, validate_default=True
    )
    lmfit_model: Optional[Model] = None

    @property
    def has_substrate(self):
        if not self.lmfit_model.components:
            return False
        comps = set(map(lambda x: x.prefix, self.lmfit_model.components))
        substrate_comps = set(
            [i.lmfit_model.prefix for i in self.substrate_peaks.values()]
        )
        return substrate_comps.issubset(comps)

    def add_substrate(self):
        if self.has_substrate:
            warn(f"{self.__class__.__name__} already has substrate.", BaseModelWarning)
            return

        for name in self.substrate_peaks.keys():
            self.peaks += SEP + name
        self.check_lmfit_model()

    def remove_substrate(self):
        if not self.has_substrate:
            warn(
                f"{self.__class__.__name__} has no substrate to remove.",
                BaseModelWarning,
            )
            return
        _peaks = self.peaks.split(SEP)
        for name in self.substrate_peaks.keys():
            _peaks.remove(name)
        self.peaks = SEP.join(_peaks)
        self.check_lmfit_model()

    @property
    def substrate_peaks(self):
        return {k: val for k, val in self.default_peaks.items() if val.is_substrate}

    @model_validator(mode="after")
    def check_peaks_in_default_peaks(self) -> "BaseModelCollection":
        peak_names = self.peaks.split(SEP)
        default_peak_names = self.default_peaks.keys()
        assert set(peak_names).union(set(default_peak_names))
        return self

    @model_validator(mode="after")
    def check_lmfit_model(self) -> "BaseModelCollection":
        lmfit_model = self.construct_lmfit_model(self.peaks, self.default_peaks)
        self.lmfit_model = lmfit_model
        return self

    def construct_lmfit_model(self, peaks, default_peaks) -> "Model":
        peak_names = peaks.split(SEP)
        base_peaks = [default_peaks[i] for i in peak_names if i in default_peaks]
        if not base_peaks:
            return GaussianModel()
        lmfit_model = construct_lmfit_model_from_base_peaks(base_peaks)
        return lmfit_model
