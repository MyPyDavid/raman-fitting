from typing import List

from raman_fitting.models.splitter import RegionNames
from raman_fitting.imports.spectrumdata_parser import SpectrumReader
from raman_fitting.processing.post_processing import SpectrumProcessor
from raman_fitting.imports.models import RamanFileInfo
from .models import (
    AggregatedSampleSpectrum,
    PreparedSampleSpectrum,
)

from loguru import logger

from raman_fitting.config.path_settings import CLEAN_SPEC_REGION_NAME_PREFIX
from ..imports.spectrum.spectra_collection import SpectraDataCollection


def prepare_aggregated_spectrum_from_files(
    region_name: RegionNames, raman_files: List[RamanFileInfo]
) -> AggregatedSampleSpectrum | None:
    select_region_key = f"{CLEAN_SPEC_REGION_NAME_PREFIX}{region_name}"
    clean_data_for_region = []
    data_sources = []
    for i in raman_files:
        read = SpectrumReader(i.file)
        processed = SpectrumProcessor(read.spectrum)
        prepared_spec = PreparedSampleSpectrum(
            file_info=i, read=read, processed=processed
        )
        data_sources.append(prepared_spec)
        selected_clean_data = processed.clean_spectrum.spec_regions[select_region_key]
        clean_data_for_region.append(selected_clean_data)
    if not clean_data_for_region:
        logger.warning(
            f"prepare_mean_data_for_fitting received no files. {region_name}"
        )
        return
    spectra_collection = SpectraDataCollection(
        spectra=clean_data_for_region, region_name=region_name
    )
    aggregated_spectrum = AggregatedSampleSpectrum(
        sources=data_sources, spectrum=spectra_collection.mean_spectrum
    )
    return aggregated_spectrum
