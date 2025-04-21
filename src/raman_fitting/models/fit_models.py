from dataclasses import dataclass, field
import time
from functools import cached_property

from pydantic import (
    BaseModel,
    PrivateAttr,
    model_validator,
    Field,
    ConfigDict,
    computed_field,
)
from lmfit import Model as LMFitModel
from lmfit.model import ModelResult

from raman_fitting.config import settings
from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames
from raman_fitting.models.post_deconvolution.calculate_params import (
    calculate_ratio_of_unique_vars_in_results,
)

from raman_fitting.models.spectrum import SpectrumData


class SpectrumFitModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    spectrum: SpectrumData = Field(repr=False)
    model: BaseLMFitModel = Field(repr=False)
    region: RegionNames
    fit_kwargs: dict = Field(default_factory=dict, repr=False)
    reuse_params: bool = Field(default=False, repr=False)

    # Private attributes using PrivateAttr
    _fit_result: ModelResult | None = PrivateAttr(default=None)
    _elapsed_seconds: float | None = PrivateAttr(default=None)
    _param_result: dict | None = PrivateAttr(default=None)

    @model_validator(mode="after")
    def match_region_names(self) -> "SpectrumFitModel":
        if self.model.region_name != self.spectrum.region:
            raise ValueError(
                f"Region names do not match {self.model.region_name} and {self.spectrum.region}"
            )
        return self

    @model_validator(mode="after")
    def test_if_spectrum_has_model_region(self) -> "SpectrumFitModel":
        model_region = self.model.region_name
        region_limits = settings.default_regions[model_region]

        # Check if the spectrum data is not empty
        if not (self.spectrum.ramanshift.size > 0 and self.spectrum.intensity.size > 0):
            raise ValueError("Spectrum is empty.")

        center_params = [
            i.param_hints.get("center", {}).get("value", 0)
            for i in self.model.lmfit_model.components
        ]

        # Collect invalid center parameters
        invalid_region_params = [
            param
            for param in center_params
            if not (region_limits.min <= param <= region_limits.max)
        ]
        if invalid_region_params:
            raise ValueError(
                f"Model parameters {invalid_region_params} do not fall within the region limits "
                f"({region_limits.min}, {region_limits.max})."
            )

        # Collect center parameters not covered by the spectrum's Raman shift data
        invalid_spectrum_params = [
            param
            for param in center_params
            if not (
                self.spectrum.ramanshift.min()
                <= param
                <= self.spectrum.ramanshift.max()
            )
        ]
        if invalid_spectrum_params:
            raise ValueError(
                f"Model parameters {invalid_spectrum_params} are not covered by the spectrum's "
                f"Raman shift data range ({self.spectrum.ramanshift.min()}, {self.spectrum.ramanshift.max()})."
            )

        return self

    def run(self) -> None:
        self._fit_result, self._elapsed_seconds, self._param_result = (
            run_fit_and_process_results(
                self.spectrum, self.model.lmfit_model, self.fit_kwargs
            )
        )

    @computed_field
    @cached_property
    def fit_result(self) -> ModelResult:
        return self._fit_result

    @computed_field
    @cached_property
    def elapsed_seconds(self) -> float | None:
        return self._elapsed_seconds

    @computed_field(repr=False)
    @cached_property
    def param_result(self) -> dict | None:
        return self._param_result


@dataclass
class SpectrumFitModelRegistry:
    spec_fit_model_registry: dict[str, SpectrumFitModel] = field(default_factory=dict)

    def add_fit(
        self, spec_fit_model: SpectrumFitModel, name: str | None = None
    ) -> None:
        name = name if name is not None else spec_fit_model.model.name
        self.spec_fit_model_registry[name] = spec_fit_model


def call_fit_on_model(
    model: LMFitModel, spectrum: SpectrumData, method="leastsq", **kwargs
) -> ModelResult:
    # ideas: improve fitting loop so that starting parameters from modelX and modelX+Si are shared, faster...
    init_params = model.make_params()
    x, y = spectrum.ramanshift, spectrum.intensity
    out = model.fit(y, init_params, x=x, method=method, **kwargs)  # 'leastsq'
    return out


def run_fit(
    spectrum: SpectrumData, lmfit_model: LMFitModel, method: str = "leastsq", **kwargs
) -> tuple[ModelResult, float]:
    start_time = time.time()
    fit_result = call_fit_on_model(lmfit_model, spectrum, method=method, **kwargs)
    end_time = time.time()
    elapsed_seconds = abs(start_time - end_time)
    return fit_result, elapsed_seconds


def run_fit_and_process_results(
    spectrum: SpectrumData, lmfit_model: LMFitModel, fit_kwargs: dict
) -> tuple[ModelResult, float, dict]:
    fit_result, elapsed_seconds = run_fit(spectrum, lmfit_model, **fit_kwargs)
    param_results = fit_result.params.valuesdict()
    param_results["ratios"] = calculate_ratio_of_unique_vars_in_results(
        fit_result.params.valuesdict(), raise_exception=False
    )
    param_results["elapsed_time_s"] = elapsed_seconds
    return fit_result, elapsed_seconds, param_results
