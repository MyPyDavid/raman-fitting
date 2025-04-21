from dataclasses import dataclass
from operator import itemgetter

from typing import Sequence
from pydantic import ValidationError

from raman_fitting.delegators.errors import processing_errors
from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.models.deconvolution.base_model import (
    LMFitModelCollection,
    BaseLMFitModel,
)
from raman_fitting.delegators.models import (
    AggregatedSampleSpectrumFitResult,
    PreparedSampleSpectrum,
)
from raman_fitting.delegators.pre_processing import (
    prepare_aggregated_spectrum_from_files,
    select_and_prepare_aggregated_spectrum_for_region,
)
from raman_fitting.imports.files.models import RamanFileInfo
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames
from raman_fitting.models.fit_models import SpectrumFitModel

from loguru import logger


def run_fit_over_selected_models(
    raman_files: Sequence[RamanFileInfo],
    models: LMFitModelCollection,
    reuse_params: bool = True,
) -> dict[RegionNames, AggregatedSampleSpectrumFitResult] | None:
    results = {}
    # First load in the data from files
    # Check and validate data
    # Then run

    prepared_spectra = prepare_aggregated_spectrum_from_files(raman_files)

    if not prepared_spectra:
        errors = ",".join(map(str, processing_errors.get_errors_for_files(raman_files)))

        logger.error(f"These files do not contain any valid data: {errors}")
        return None

    for region, models_for_region in models.items():
        try:
            region = RegionNames(region)
        except ValueError as exc:
            logger.error(f"Region name {region}  not found. {exc}")
            continue
        if not models_for_region:
            logger.info(f"There are no models defined for region {region}.")
            continue

        region_fit_result = run_fit_for_region_on_prepared_spectra(
            region, models_for_region, prepared_spectra, reuse_params=reuse_params
        )
        if region_fit_result:
            results[region] = region_fit_result
        else:
            logger.debug(f"Region {region} did not yield any fit results.")

    return results


def run_fit_for_region_on_prepared_spectra(
    region: RegionNames,
    models: dict[str, BaseLMFitModel],
    spectra: list[PreparedSampleSpectrum],
    reuse_params: bool = True,
) -> AggregatedSampleSpectrumFitResult | None:
    try:
        aggregated_spectrum = select_and_prepare_aggregated_spectrum_for_region(
            region, spectra
        )
        if aggregated_spectrum is None:
            logger.debug(f"Aggregated spectrum is None, {region}")
            return
    except ValueError:
        logger.error(f"Can not prepare aggregated_spectrum for: {region}")
        return

    spectrum_fit_models, fit_prep_errors = create_fit_models_with_spectrum_for_models(
        aggregated_spectrum.spectrum, models, reuse_params=reuse_params
    )

    try:
        handle_fit_errors(fit_prep_errors, raise_errors=True)
    except ValueError as e:
        logger.error(f"Errors in preparing fits for {region}. {e}")
        return

    if not spectrum_fit_models:
        logger.info(f"No spectra selected for {region}")

    fit_model_results, fit_errors = run_fit_loop_single(spectrum_fit_models)
    if fit_errors:
        handle_fit_errors(fit_errors, raise_errors=False)

    try:
        return AggregatedSampleSpectrumFitResult(
            region=region,
            aggregated_spectrum=aggregated_spectrum,
            fit_model_results=fit_model_results,
        )
    except ValueError as e:
        breakpoint()
        print(e)


@dataclass
class FitError:
    model_name: str
    region: str
    spectrum: SpectrumData
    error: Exception


def create_fit_models_with_spectrum_for_models(
    spectrum: SpectrumData,
    models: dict[str, BaseLMFitModel],
    reuse_params=False,
    **fit_kwargs,
) -> tuple[list[SpectrumFitModel], list[FitError]]:
    spec_fits = []
    errors = []
    for model_name, model in models.items():
        try:
            spec_fits.append(
                SpectrumFitModel(
                    spectrum=spectrum,
                    model=model,
                    region=model.region_name,
                    reuse_params=reuse_params,
                    fit_kwargs=fit_kwargs,
                )
            )
        except ValidationError as e:
            logger.error(
                f"Could not initialize fit model {model_name} to spectrum {model.region_name}.{e}"
            )
            errors.append(FitError(model_name, model.region_name.name, spectrum, e))
            continue
    return spec_fits, errors


def run_fit_loop_single(
    spec_fits: list[SpectrumFitModel],
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
