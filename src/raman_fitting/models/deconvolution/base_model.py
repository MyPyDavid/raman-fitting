""" The members of the validated collection of BasePeaks are assembled here into fitting Models"""
import logging
from typing import Optional, Dict
from warnings import warn

from lmfit.models import Model as LMFitModel
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
)

from raman_fitting.models.deconvolution.base_peak import (
    BasePeak,
    get_peaks_from_peak_definitions,
)
from raman_fitting.models.deconvolution.lmfit_parameter import (
    construct_lmfit_model_from_components,
)
from raman_fitting.config.default_models import load_default_model_and_peak_definitions
from raman_fitting.models.splitter import WindowNames

logger = logging.getLogger(__name__)

SUBSTRATE_PEAK = "Si1_peak"
SEP = "+"
SUFFIX = "_"


class BaseLMFitModelWarning(UserWarning):
    pass


class BaseLMFitModel(BaseModel):
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
    peak_collection: Dict[str, BasePeak] = Field(
        default_factory=get_peaks_from_peak_definitions,
        validate_default=True,
        repr=False,
    )
    lmfit_model: LMFitModel = Field(None, init_var=False, repr=False)
    window_name: WindowNames

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
            warn(
                f"{self.__class__.__name__} already has substrate.",
                BaseLMFitModelWarning,
            )
            return

        for name in self.substrate_peaks.keys():
            self.peaks += SEP + name
        self.check_lmfit_model()

    def remove_substrate(self):
        if not self.has_substrate:
            warn(
                f"{self.__class__.__name__} has no substrate to remove.",
                BaseLMFitModelWarning,
            )
            return
        _peaks = self.peaks.split(SEP)
        for name in self.substrate_peaks.keys():
            _peaks.remove(name)
        self.peaks = SEP.join(_peaks)
        self.check_lmfit_model()

    @property
    def substrate_peaks(self):
        return {k: val for k, val in self.peak_collection.items() if val.is_substrate}

    @model_validator(mode="after")
    def check_peaks_in_peak_collection(self) -> "BaseLMFitModel":
        peak_names_split = self.peaks.split(SEP)
        default_peak_names = self.peak_collection.keys()
        valid_peaks = set(peak_names_split).union(set(default_peak_names))
        assert valid_peaks
        new_peak_names = SEP.join([i for i in peak_names_split if i in valid_peaks])
        self.peaks = new_peak_names
        return self

    @model_validator(mode="after")
    def check_lmfit_model(self) -> "BaseLMFitModel":
        lmfit_model = construct_lmfit_model(self.peaks, self.peak_collection)
        self.lmfit_model = lmfit_model
        return self


def construct_lmfit_model(
    peaks: str, peak_collection: Dict[str, BasePeak]
) -> LMFitModel:
    peak_names = peaks.split(SEP)
    base_peaks = [peak_collection[i] for i in peak_names if i in peak_collection]
    if not base_peaks:
        raise ValueError(f"Could not find matching peaks for {peaks}")
    base_peaks_lmfit = [i.lmfit_model for i in base_peaks]
    lmfit_model = construct_lmfit_model_from_components(base_peaks_lmfit)
    return lmfit_model


def get_models_and_peaks_from_definitions(
    models_and_peaks_definitions: Optional[Dict] = None,
) -> Dict[str, Dict[str, BaseLMFitModel]]:
    if models_and_peaks_definitions is None:
        models_and_peaks_definitions = load_default_model_and_peak_definitions()
    peak_collection = get_peaks_from_peak_definitions(
        peak_definitions=models_and_peaks_definitions
    )
    models_settings = {
        k: val.get("models") for k, val in models_and_peaks_definitions.items()
    }
    all_models = {}
    for window_name, window_model_settings in models_settings.items():
        all_models[window_name] = {}
        for model_name, model_peaks in window_model_settings.items():
            all_models[window_name][model_name] = BaseLMFitModel(
                name=model_name,
                peaks=model_peaks,
                peak_collection=peak_collection,
                window_name=window_name,
            )
    return all_models


def main():
    models = get_models_and_peaks_from_definitions()
    # breakpoint()
    print("Models: ", len(models))


if __name__ == "__main__":
    main()
