from dataclasses import dataclass
import logging

from raman_fitting.config.filepath_helper import load_default_peak_toml_files
from raman_fitting.deconvolution_models.base_model import get_models_from_settings


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
        if not self.lmfit_models and self.settings:
            self.lmfit_models = get_models_from_settings(self.settings)

    def __repr__(self):
        _t = ", ".join(map(str, self.lmfit_models.keys()))
        _t += "\n"
        _t += "\n".join(map(str, self.lmfit_models.values()))
        return _t


def main():
    from raman_fitting.config.filepath_helper import load_default_peak_toml_files

    settings = load_default_peak_toml_files()
    print("settings: ", settings)
    models = InitializeModels()
    print(models)
    # breakpoint()


if __name__ == "__main__":
    main()
