from dataclasses import dataclass
import logging

from raman_fitting.config.filepath_helper import load_default_peak_toml_files
from raman_fitting.deconvolution_models.base_model import SEP
from raman_fitting.deconvolution_models.base_peak import BasePeak

logger = logging.getLogger(__name__)


@dataclass
class InitializeModels:
    """
    This class will initialize and validate the different fitting models.
    The models are of type lmfit.model.CompositeModel and stored in a dict with names
    for the models as keys.
    """

    settings: dict = None
    peaks: dict = None
    lmfit_models: dict = None

    def __post_init__(self):
        self.settings = self.settings or {}
        self.peaks = self.peaks or {}
        self.lmfit_models = self.lmfit_models or {}
        if not self.settings:
            self.settings = load_default_peak_toml_files()
        if not self.lmfit_models:
            self.lmfit_models = self.construct_lmfit_models(self.settings)

    def construct_basepeaks(self, settings: dict):
        peaks = {}
        peak_items = {
            **settings["first_order"]["peaks"],
            **settings["second_order"]["peaks"],
        }.items()
        for k, v in peak_items:
            peaks.update({k: BasePeak(**v)})
        return peaks

    def construct_lmfit_models(self, settings: dict):
        peaks = self.construct_basepeaks(settings)

        model_items = {
            **settings["first_order"]["models"],
            **settings["second_order"]["models"],
        }.items()
        models = {}
        for model_name, model_comp in model_items:
            peak_comps = [peaks[i] for i in model_comp.split(SEP)]
            lmfit_comp_model = sum(
                map(lambda x: x.lmfit_model, peak_comps), peak_comps.pop().lmfit_model
            )
            models[model_name] = lmfit_comp_model
        return models

    def __repr__(self):
        _t = ", ".join(map(str, self.lmfit_models.keys()))
        _t += "\n"
        _t += "\n".join(map(str, self.lmfit_models.values()))
        return _t


def main():
    from raman_fitting.config.filepath_helper import load_default_peak_toml_files

    settings = load_default_peak_toml_files()
    models = InitializeModels()
    print(models)
    breakpoint()


if __name__ == "__main__":
    main()
