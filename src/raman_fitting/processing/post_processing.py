from dataclasses import dataclass
from typing import Protocol

from raman_fitting.models.spectrum import SpectrumData

from .baseline_subtraction import subtract_baseline_from_split_spectrum
from .filter import filter_spectrum
from .despike import SpectrumDespiker
from ..models.splitter import SplitSpectrum
from .normalization import normalize_split_spectrum


class PreProcessor(Protocol):
    def process_spectrum(self, spectrum: SpectrumData = None): ...


class PostProcessor(Protocol):
    def process_spectrum(self, split_spectrum: SplitSpectrum = None): ...


@dataclass
class SpectrumProcessor:
    spectrum: SpectrumData
    processed: bool = False
    clean_spectrum: SplitSpectrum | None = None

    def __post_init__(self):
        processed_spectrum = self.process_spectrum()
        self.clean_spectrum = processed_spectrum
        self.processed = True

    def process_spectrum(self) -> SplitSpectrum:
        pre_processed_spectrum = self.pre_process_intensity(spectrum=self.spectrum)
        post_processed_spectra = self.post_process_spectrum(
            spectrum=pre_processed_spectrum
        )
        return post_processed_spectra

    def pre_process_intensity(self, spectrum: SpectrumData = None) -> SpectrumData:
        filtered_spectrum = filter_spectrum(spectrum=spectrum)
        despiker = SpectrumDespiker(spectrum=filtered_spectrum)
        return despiker.processed_spectrum

    def post_process_spectrum(self, spectrum: SpectrumData = None) -> SplitSpectrum:
        split_spectrum = SplitSpectrum(spectrum=spectrum)
        baseline_subtracted = subtract_baseline_from_split_spectrum(
            split_spectrum=split_spectrum
        )
        normalized_spectra = normalize_split_spectrum(
            split_spectrum=baseline_subtracted
        )
        return normalized_spectra
