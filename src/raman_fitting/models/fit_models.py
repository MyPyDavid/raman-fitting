import logging
from typing import Dict
import time

from pydantic import BaseModel, model_validator, Field, ConfigDict
from lmfit import Model as LMFitModel
from lmfit.model import ModelResult

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.deconvolution.spectrum_regions import WindowNames

from raman_fitting.models.spectrum import SpectrumData

logger = logging.getLogger(__name__)


FIT_RESULT_ATTR_LIST = (
    "chisqr",
    "redchi",
    "bic",
    "aic",
    "method",
    "message",
    "success",
    "nfev",
)


class SpectrumFitModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    spectrum: SpectrumData
    model: BaseLMFitModel
    window: WindowNames
    fit_kwargs: Dict = Field(default_factory=dict)
    fit_result: ModelResult = Field(None, init_var=False)
    elapsed_time: float = Field(0, init_var=False, repr=False)

    @model_validator(mode="after")
    def match_window_names(self):
        model_window = self.model.window_name
        spec_window = self.spectrum.window_name
        if model_window != spec_window:
            raise ValueError(
                f"Window names do not match {model_window} and {spec_window}"
            )
        return self

    def run_fit(self) -> None:
        if "method" not in self.fit_kwargs:
            self.fit_kwargs["method"] = "leastsq"
        lmfit_model = self.model.lmfit_model
        start_time = time.time()
        fit_result = run_fit(lmfit_model, self.spectrum, **self.fit_kwargs)
        end_time = time.time()
        elapsed_seconds = abs(start_time - end_time)
        self.elapsed_time = elapsed_seconds
        self.fit_result = fit_result


    def process_fit_results(self):
        #  TODO add parameter post processing steps
        self.fit_result

        fit_attrs = {
            f"lmfit_{i}": getattr(self.fit_result, i) for i in FIT_RESULT_ATTR_LIST
        }
        self.add_ratio_params()

        self.result.update(fit_attrs)


def run_fit(
    model: LMFitModel, spectrum: SpectrumData, method="leastsq", **kws
) -> ModelResult:
    # ideas: improve fitting loop so that starting parameters from modelX and modelX+Si are shared, faster...
    init_params = model.make_params()
    x, y = spectrum.ramanshift, spectrum.intensity
    out = model.fit(y, init_params, x=x, method=method)  # 'leastsq'
    return out


if __name__ == "__main__":
    from raman_fitting.config.base_settings import settings

    test_fixtures = list(settings.internal_paths.example_fixtures.glob("*txt"))
    file = [i for i in test_fixtures if "_pos4" in i.stem][0]
    from raman_fitting.imports.spectrumdata_parser import SpectrumReader

    specread = SpectrumReader(file)

    from raman_fitting.processing.post_processing import SpectrumProcessor

    spectrum_processor = SpectrumProcessor(specread.spectrum)
    clean_spec_1st_order = spectrum_processor.clean_spectrum.spec_windows[
        "savgol_filter_raw_window_first_order"
    ]
    clean_spec_1st_order.window_name = "first_order"

    from raman_fitting.models.deconvolution.base_model import (
        get_models_and_peaks_from_definitions,
    )

    models = get_models_and_peaks_from_definitions()
    model_2peaks = models["first_order"]["2peaks"]
    spec_fit = SpectrumFitModel(
        **{"spectrum": clean_spec_1st_order, "model": model_2peaks}
    )
    spec_fit.run_fit()
    print(spec_fit.fit_result.best_values)
    spec_fit.fit_result.plot(show_init=True)
