from typing import List

from raman_fitting.config.path_settings import (
    CLEAN_SPEC_WINDOW_NAME_PREFIX,
)
from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.models.splitter import WindowNames
from raman_fitting.imports.spectrumdata_parser import SpectrumReader
from raman_fitting.processing.post_processing import SpectrumProcessor
from raman_fitting.imports.models import RamanFileInfo
from .models import (
    AggregatedSampleSpectrum,
    PreparedSampleSpectrum,
)

import numpy as np
from loguru import logger


def prepare_aggregated_spectrum_from_files(
    window_name: WindowNames, raman_files: List[RamanFileInfo]
) -> AggregatedSampleSpectrum | None:
    selected_processed_data = f"{CLEAN_SPEC_WINDOW_NAME_PREFIX}{window_name}"
    clean_data_for_window = {}
    data_sources = []
    for i in raman_files:
        read = SpectrumReader(i.file)
        processed = SpectrumProcessor(read.spectrum)
        prepared_spec = PreparedSampleSpectrum(
            file_info=i, read=read, processed=processed
        )
        data_sources.append(prepared_spec)
        selected_clean_data = processed.clean_spectrum.spec_regions[
            selected_processed_data
        ]
        clean_data_for_window[i.file] = selected_clean_data

    if not clean_data_for_window:
        logger.info("prepare_mean_data_for_fitting received no files.")
        return
    # TODO wrap this in a ProcessedSpectraCollection model
    mean_int = np.mean(
        np.vstack([i.intensity for i in clean_data_for_window.values()]), axis=0
    )
    mean_ramanshift = np.mean(
        np.vstack([i.ramanshift for i in clean_data_for_window.values()]), axis=0
    )
    source_files = list(map(str, clean_data_for_window.keys()))
    mean_spec = SpectrumData(
        **{
            "ramanshift": mean_ramanshift,
            "intensity": mean_int,
            "label": f"clean_{window_name}_mean",
            "window_name": window_name,
            "source": source_files,
        }
    )
    aggregated_spectrum = AggregatedSampleSpectrum(
        sources=data_sources, spectrum=mean_spec
    )
    return aggregated_spectrum
