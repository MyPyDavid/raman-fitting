from dataclasses import dataclass
import logging
from typing import Protocol

from raman_fitting.models.spectrum import SpectrumData

from .baseline_subtraction import subtract_baseline_from_split_spectrum
from .filter import filter_spectrum
from .despike import SpectrumDespiker
from ..models.splitter import SplitSpectrum
from .normalization import normalize_split_spectrum

logger = logging.getLogger(__name__)


POST_PROCESS_KWARGS = {"filter_name": "savgol_"}


class PostProcessor(Protocol):
    def process_spectrum(self, spectrum: SpectrumData): ...


@dataclass
class SpectrumProcessor:
    spectrum: SpectrumData
    processed: bool = False

    def __post_init__(self):
        processed_spectrum = self.process_spectrum()
        self.processed_spectrum = processed_spectrum
        self.clean_spectrum = processed_spectrum
        self.processed = True

    def process_spectrum(self) -> SplitSpectrum:
        pre_processed_spectrum = self.pre_process_intensity()
        post_processed_spectra = self.post_process_spectrum(pre_processed_spectrum)
        return post_processed_spectra

    def pre_process_intensity(self) -> SpectrumData:
        filtered_spectrum = filter_spectrum(self.spectrum)
        despiker = SpectrumDespiker(**{"spectrum": filtered_spectrum})
        return despiker.despiked_spectrum

    def post_process_spectrum(self, spectrum: SpectrumData) -> SplitSpectrum:
        split_spectrum = SplitSpectrum(spectrum=spectrum)
        baseline_subtracted = subtract_baseline_from_split_spectrum(split_spectrum)
        normalized_spectra = normalize_split_spectrum(baseline_subtracted)
        return normalized_spectra
