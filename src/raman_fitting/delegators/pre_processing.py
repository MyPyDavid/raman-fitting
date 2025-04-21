from typing import Sequence

from loguru import logger

from raman_fitting.models.splitter import RegionNames, SpectrumFileRegionSelection
from raman_fitting.imports.models import SpectrumReader
from raman_fitting.processing.post_processing import SpectrumProcessor
from raman_fitting.imports.files.models import RamanFileInfo
from .models import (
    AggregatedSampleSpectrum,
    PreparedSampleSpectrum,
)

from raman_fitting.config import settings
from raman_fitting.imports.spectrum.spectra_collection import SpectraDataCollection
from ..imports.errors import FileProcessingError, ErrorType
from ..imports.spectrum.parser import load_and_parse_spectrum_from_file
from .errors import processing_errors
from .registry import processed_files


def prepare_aggregated_spectrum_from_files(
    raman_files: Sequence[RamanFileInfo],
) -> list[PreparedSampleSpectrum]:
    prepared_spectra = []
    for i in raman_files:
        if i.filepath in processed_files:
            prepared_spectrum = processed_files[i.filepath]
        else:
            prepared_spectrum = process_and_prepare_spectrum_from_file(i)
            processed_files[i.filepath] = prepared_spectrum

        if prepared_spectrum is not None:
            prepared_spectra.append(prepared_spectrum)
    return prepared_spectra


def select_and_prepare_aggregated_spectrum_for_region(
    region_name: RegionNames, prepared_spectra: list[PreparedSampleSpectrum]
) -> AggregatedSampleSpectrum:
    spectra_for_region = []
    data_sources = []
    for spectrum in prepared_spectra:
        selector = SpectrumFileRegionSelection(
            file=spectrum.file_info, region=region_name
        )
        if selector in processing_errors:
            logger.debug(f"Skipped {selector}")
        try:
            region_spec = spectrum.processed.processed_spectra.get_spec_for_region(
                region_name
            )
            spectra_for_region.append(region_spec)
            data_sources.append(spectrum)
        except ValueError:
            msg = f"Could not get region {region_name} from processing {spectrum}"
            logger.warning(msg)
            processing_errors.add_error(
                FileProcessingError(
                    spectrum.file_info.filepath,
                    ErrorType.REGION_ERROR,
                    msg,
                    region_name,
                )
            )

    if not spectra_for_region:
        logger.error(
            f"prepare_mean_data_for_fitting received no valid files. {region_name}"
        )
        raise ValueError("no valid data for aggregation")

    spectra_collection = SpectraDataCollection(
        spectra=spectra_for_region, region_name=region_name
    )
    aggregated_spectrum = AggregatedSampleSpectrum(
        prepared_sources=data_sources, spectrum=spectra_collection.mean_spectrum
    )
    return aggregated_spectrum


def process_and_prepare_spectrum_from_file(
    file: RamanFileInfo,
) -> PreparedSampleSpectrum | FileProcessingError:
    if file in processing_errors:
        logger.debug(f"Skipped due to errors: {file}")
        return processing_errors.get_errors_for_files(file)

    parsed_spectrum_or_error = load_and_parse_spectrum_from_file(
        file=file.filepath,
    )
    if isinstance(parsed_spectrum_or_error, FileProcessingError):
        processing_errors.add_error(parsed_spectrum_or_error)
        return parsed_spectrum_or_error

    parsed_spectrum = parsed_spectrum_or_error

    read = SpectrumReader(filepath=file.filepath, spectrum=parsed_spectrum)

    processed = SpectrumProcessor(
        spectrum=read.spectrum, region_limits=settings.default_regions
    )

    return PreparedSampleSpectrum(file_info=file, read=read, processed=processed)
