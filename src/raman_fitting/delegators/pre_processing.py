from typing import Sequence

from loguru import logger

from raman_fitting.models.splitter import RegionNames
from raman_fitting.imports.spectrumdata_parser import SpectrumReader
from raman_fitting.processing.post_processing import SpectrumProcessor
from raman_fitting.imports.files.models import RamanFileInfo
from .models import (
    AggregatedSampleSpectrum,
    PreparedSampleSpectrum,
)

from raman_fitting.config import settings
from raman_fitting.imports.spectrum.spectra_collection import SpectraDataCollection


def prepare_aggregated_spectrum_from_files(
    region_name: RegionNames, raman_files: Sequence[RamanFileInfo]
) -> AggregatedSampleSpectrum | None:
    clean_data_for_region = []
    data_sources = []
    for i in raman_files:
        read = SpectrumReader(i.file)

        if read.spectrum is None:
            logger.error(f"Could not read {i.file}")
            continue

        processed = SpectrumProcessor(
            spectrum=read.spectrum, region_limits=settings.default_regions
        )

        prepared_spec = PreparedSampleSpectrum(
            file_info=i, read=read, processed=processed
        )
        data_sources.append(prepared_spec)
        try:
            clean_data_for_region.append(
                processed.processed_spectra.get_spec_for_region(region_name)
            )
        except ValueError:
            logger.warning(
                f"Could not get region {region_name} from processing {i.file}"
            )

    if not clean_data_for_region:
        logger.warning(
            f"prepare_mean_data_for_fitting received no valid files. {region_name}"
        )
        raise ValueError("no valid data for aggregation")

    spectra_collection = SpectraDataCollection(
        spectra=clean_data_for_region, region_name=region_name
    )
    aggregated_spectrum = AggregatedSampleSpectrum(
        sources=data_sources, spectrum=spectra_collection.mean_spectrum
    )
    return aggregated_spectrum
