from dataclasses import dataclass, field
from typing import Protocol

from pydantic import ValidationError

from raman_fitting.models.spectrum import SpectrumData

from .baseline_subtraction import subtract_baseline_from_split_spectrum
from .filter import filter_spectrum
from .despike import despike_spectrum_data
from ..models.deconvolution.spectrum_regions import (
    SpectrumRegionsLimitsSet,
)
from ..models.splitter import SplitSpectrum
from .normalization import normalize_split_spectrum


class PreProcessor(Protocol):
    def process_spectrum(self, spectrum: SpectrumData | None = None): ...


class PostProcessor(Protocol):
    def process_spectrum(self, split_spectrum: SplitSpectrum | None = None): ...


@dataclass
class SpectrumProcessor:
    """performs  pre-processing, post-, and"""

    spectrum: SpectrumData = field(repr=False)
    region_limits: SpectrumRegionsLimitsSet = field(repr=False)
    processed: bool = False
    processed_spectra: SplitSpectrum | None = None

    def __post_init__(self):
        try:
            self.processed_spectra = self.process_spectrum()
            self.processed = True
        except ValueError as e:
            raise e from e
        except ValidationError as e:
            raise e from e

    def process_spectrum(self) -> SplitSpectrum:
        return post_process_spectrum(
            split_process_spectrum(
                pre_process_intensity(spectrum=self.spectrum), self.region_limits
            )
        )


def pre_process_intensity(spectrum: SpectrumData) -> SpectrumData:
    return despike_spectrum_data(filter_spectrum(spectrum=spectrum))


def split_process_spectrum(
    spectrum: SpectrumData, region_limits: SpectrumRegionsLimitsSet
) -> SplitSpectrum:
    return SplitSpectrum(spectrum=spectrum, region_limits=region_limits)


def post_process_spectrum(split_spectrum: SplitSpectrum) -> SplitSpectrum:
    return normalize_split_spectrum(
        subtract_baseline_from_split_spectrum(split_spectrum)
    )
