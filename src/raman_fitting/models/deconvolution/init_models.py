from dataclasses import dataclass, field
import logging
from typing import Dict

from raman_fitting.config.filepath_helper import load_default_model_and_peak_definitions
from raman_fitting.models.deconvolution.base_model import (
    get_models_and_peaks_from_definitions,
)
from .base_model import BaseLMFitModel

logger = logging.getLogger(__name__)


@dataclass
class InitializeModels:
    """
    This class will initialize and validate the different fitting models.
    The models are of type lmfit.model.CompositeModel and stored in a dict with names
    for the models as keys.
    """

    settings: dict = field(default_factory=dict)
    peaks: dict = field(default_factory=dict)
    lmfit_models: Dict[str, Dict[str, BaseLMFitModel]] = None

    def __post_init__(self):
        self.settings = self.settings or {}
        self.peaks = self.peaks or {}
        self.lmfit_models = self.lmfit_models or {}
        if not self.settings:
            self.settings = load_default_model_and_peak_definitions()
        if not self.lmfit_models and self.settings:
            self.lmfit_models = get_models_and_peaks_from_definitions(self.settings)

    def __repr__(self):
        _t = ", ".join(map(str, self.lmfit_models.keys()))
        _t += "\n"
        _t += "\n".join(map(str, self.lmfit_models.values()))
        return _t


def main():
    from raman_fitting.config.filepath_helper import (
        load_default_model_and_peak_definitions,
    )

    settings = load_default_model_and_peak_definitions()
    print("settings: ", settings)
    models = InitializeModels()
    print(models)
    # breakpoint()


if __name__ == "__main__":
    main()
