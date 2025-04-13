from dataclasses import dataclass
from operator import itemgetter

from typing import Sequence
from pydantic import ValidationError


from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.models.deconvolution.base_model import LMFitModelCollection
from raman_fitting.delegators.models import AggregatedSampleSpectrumFitResult
from raman_fitting.delegators.pre_processing import (
    prepare_aggregated_spectrum_from_files,
)
from raman_fitting.imports.files.models import RamanFileInfo
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames
from raman_fitting.models.fit_models import SpectrumFitModel

from loguru import logger


def run_fit_over_selected_models(
    raman_files: Sequence[RamanFileInfo],
    models: LMFitModelCollection,
    use_multiprocessing: bool = False,
    reuse_params: bool = True,
) -> dict[RegionNames, AggregatedSampleSpectrumFitResult]:
    if use_multiprocessing:
        from raman_fitting.delegators.run_fit_multi import run_fit_multiprocessing

    results = {}
    for region_name, model_region_grp in models.items():
        try:
            region_name = RegionNames(region_name)
        except ValueError as exc:
            logger.error(f"Region name {region_name} not found. {exc}")
            continue

        aggregated_spectrum = prepare_aggregated_spectrum_from_files(
            region_name, raman_files
        )
        if aggregated_spectrum is None:
            continue
        spec_fits, fit_prep_errors = prepare_spec_fit_regions(
            aggregated_spectrum.spectrum, model_region_grp, reuse_params=reuse_params
        )

        try:
            handle_fit_errors(fit_prep_errors, raise_errors=True)
        except ValueError as e:
            logger.error(f"Errors in preparing fits for {region_name}. {e}")
            continue

        if not spec_fits:
            logger.info(f"No spectra selected for {region_name}")

        if use_multiprocessing:
            fit_model_results = run_fit_multiprocessing(spec_fits)
        else:
            fit_model_results, fit_errors = run_fit_loop_single(spec_fits)

        handle_fit_errors(fit_errors, raise_errors=False)

        fit_region_results = AggregatedSampleSpectrumFitResult(
            region_name=region_name,
            aggregated_spectrum=aggregated_spectrum,
            fit_model_results=fit_model_results,
        )
        results[region_name] = fit_region_results
    return results


@dataclass
class FitError:
    model_name: str
    region: str
    spectrum: SpectrumData
    error: Exception


def prepare_spec_fit_regions(
    spectrum: SpectrumData, model_region_grp, reuse_params=False, **fit_kwargs
) -> tuple[list[SpectrumFitModel], list[FitError]]:
    spec_fits = []
    errors = []
    for model_name, model in model_region_grp.items():
        try:
            spec_fit = SpectrumFitModel(
                spectrum=spectrum,
                model=model,
                region=model.region_name,
                reuse_params=reuse_params,
                fit_kwargs=fit_kwargs,
            )
            spec_fits.append(spec_fit)
        except ValidationError as e:
            logger.error(
                f"Could not initialize fit model {model_name} to spectrum {model.region_name}.{e}"
            )
            errors.append(FitError(model_name, model.region_name.name, spectrum, e))
            continue
    return spec_fits, errors


def run_fit_loop_single(
    spec_fits: Sequence[SpectrumFitModel],
) -> tuple[dict[str, SpectrumFitModel], list[FitError]]:
    fit_model_results = {}
    errors: list[FitError] = []
    best_params: dict[str, float] = {}
    for spec_fit_model in spec_fits:
        #  include optional https://lmfit.github.io/lmfit-py/model.html#saving-and-loading-modelresults
        model_name = spec_fit_model.model.name
        region = spec_fit_model.region
        spectrum = spec_fit_model.spectrum
        if spec_fit_model.reuse_params and best_params:
            spec_fit_model = update_param_hints(spec_fit_model, best_params)

        try:
            spec_fit_model.run()
            logger.debug(
                f"Fit with model {model_name} on {region} success: {spec_fit_model.fit_result.success} in {spec_fit_model.elapsed_seconds:.2f}s."
            )
            fit_model_results[model_name] = spec_fit_model
            best_params = update_best_params(fit_model_results, best_params)
        except Exception as e:
            logger.error(f"Could not fit model {model_name} to spectrum {region}.{e}")
            errors.append(FitError(model_name, region, spectrum, e))

    return fit_model_results, errors


def update_param_hints(
    spec_fit_model: SpectrumFitModel, params: dict
) -> SpectrumFitModel:
    for param, value in params.items():
        spec_fit_model.model.lmfit_model.set_param_hint(param, value=value)
    return spec_fit_model


def update_best_params(
    fit_model_results: dict[str, SpectrumFitModel], best_params: dict
) -> dict:
    if not fit_model_results:
        return best_params
    best_values = [
        (i.fit_result.bic, i.fit_result.best_values) for i in fit_model_results.values()
    ]
    _best_bic, best_params = min(best_values, key=itemgetter(0))
    return best_params


def handle_fit_errors(fit_errors: Sequence[FitError], raise_errors: bool = False):
    if fit_errors:
        logger.error("Errors in fitting")
        for error in fit_errors:
            logger.error(
                f"Error fitting {error.model_name} to {error.region} with {error.spectrum}. {error.error}"
            )
        if raise_errors:
            raise ValueError("Errors in fitting")
