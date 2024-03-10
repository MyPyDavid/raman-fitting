from typing import List, Dict

from raman_fitting.delegating.run_fit_multi import run_fit_multiprocessing
from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.types import LMFitModelCollection
from raman_fitting.delegating.models import AggregatedSampleSpectrumFitResult
from raman_fitting.delegating.pre_processing import (
    prepare_aggregated_spectrum_from_files,
)
from raman_fitting.imports.models import RamanFileInfo
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames
from raman_fitting.models.fit_models import SpectrumFitModel

from loguru import logger


def run_fit_over_selected_models(
    raman_files: List[RamanFileInfo],
    models: LMFitModelCollection,
    use_multiprocessing: bool = False,
) -> Dict[RegionNames, AggregatedSampleSpectrumFitResult]:
    results = {}
    for region_name, model_region_grp in models.items():
        aggregated_spectrum = prepare_aggregated_spectrum_from_files(
            region_name, raman_files
        )
        if aggregated_spectrum is None:
            continue
        spec_fits = prepare_spec_fit_regions(
            aggregated_spectrum.spectrum, model_region_grp
        )
        if use_multiprocessing:
            fit_model_results = run_fit_multiprocessing(spec_fits)
        else:
            fit_model_results = run_fit_loop(spec_fits)
        fit_region_results = AggregatedSampleSpectrumFitResult(
            region_name=region_name,
            aggregated_spectrum=aggregated_spectrum,
            fit_model_results=fit_model_results,
        )
        results[region_name] = fit_region_results
    return results


def prepare_spec_fit_regions(
    spectrum: SpectrumData, model_region_grp
) -> List[SpectrumFitModel]:
    spec_fits = []
    for model_name, model in model_region_grp.items():
        region = model.region_name.name
        spec_fit = SpectrumFitModel(spectrum=spectrum, model=model, region=region)
        spec_fits.append(spec_fit)
    return spec_fits


def run_fit_loop(spec_fits: List[SpectrumFitModel]) -> Dict[str, SpectrumFitModel]:
    fit_model_results = {}
    for spec_fit in spec_fits:
        #  include optional https://lmfit.github.io/lmfit-py/model.html#saving-and-loading-modelresults
        spec_fit.run_fit()
        logger.debug(
            f"Fit with model {spec_fit.model.name} on {spec_fit.region} success: {spec_fit.fit_result.success} in {spec_fit.elapsed_time:.2f}s."
        )
        fit_model_results[spec_fit.model.name] = spec_fit
    return fit_model_results
