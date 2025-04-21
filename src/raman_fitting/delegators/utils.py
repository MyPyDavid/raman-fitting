from loguru import logger

from raman_fitting.delegators.models import AggregatedSampleSpectrumFitResult
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames


def log_results(
    results: dict[str, dict[str, dict[RegionNames, AggregatedSampleSpectrumFitResult]]],
    errors: list[str],
) -> None:
    """Log the results of the processing."""
    if results:
        logger.debug(f"Results: {results.keys()}")
    else:
        logger.warning("No results generated.")
    if errors:
        logger.error(f"Errors: {errors}")
