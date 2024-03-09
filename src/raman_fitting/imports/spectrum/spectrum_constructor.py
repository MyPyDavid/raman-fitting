import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import pandas as pd

from raman_fitting.imports.spectrumdata_parser import SpectrumReader
from pydantic import BaseModel

from raman_fitting.processing.post_processing import SpectrumProcessor

from raman_fitting.models.splitter import SplitSpectrum

logger = logging.getLogger(__name__)
SPECTRUM_KEYS = ("ramanshift", "intensity")


class PostProcessedSpectrum(BaseModel):
    pass


@dataclass(order=True, frozen=False)
class SpectrumDataLoader:
    """
    Raman Spectrum Loader Dataclass, reads in the file and constructs
    a clean spectrum from the data.
    A sequence of steps is performed on the raw data from SpectrumReader.
    The steps/methods are: smoothening filter, despiking and baseline correction.
    """

    file: Path = field(default_factory=Path)
    info: Dict = field(default_factory=dict, repr=False)
    # ovv: pd.DataFrame = field(default_factory=pd.DataFrame, repr=False)
    run_kwargs: Dict = field(default_factory=dict, repr=False)
    spectrum_length: int = field(default=0, init=False)
    clean_spectrum: SplitSpectrum = field(default=None, init=False)

    def __post_init__(self):
        self._qcnm = self.__class__.__qualname__
        self.register = {}  # this stores the data of each method as they are performed
        self.load_data_delegator()

    def validate_info_with_filepath(self):
        if not self.info:
            self.info = {"FilePath": self.file}
            return
        filepath_ = self.info.get("FilePath", None)
        if filepath_ and Path(filepath_) != self.file:
            raise ValueError(
                f"Mismatch in value for FilePath: {self.file} != {filepath_}"
            )

    def load_data_delegator(self):
        """calls the SpectrumReader class"""

        self.validate_info_with_filepath()
        raw_spectrum = SpectrumReader(self.file)
        self._raw_spectrum = raw_spectrum
        self.info = {**self.info, **self.run_kwargs}
        self.spectrum_length = 0
        if raw_spectrum.spectrum is None or raw_spectrum.spectrum_length == 0:
            logger.error(f"{self._qcnm} load data fail for:\n\t {self.file}")
            return

        spectrum_processor = SpectrumProcessor(raw_spectrum.spectrum)
        self.clean_spectrum = spectrum_processor.clean_spectrum
        self.spectrum_length = raw_spectrum.spectrum_length

    def set_clean_spectrum_df(self):
        if self.clean_spectrum is None:
            return

        self.clean_df = {
            k: pd.DataFrame({"ramanshift": val.ramanshift, "int": val.intensity})
            for k, val in self.clean_spectrum.items()
        }

    def plot_raw(self):
        _raw_lbls = [
            i
            for i in self.register_df.columns
            if not any(a in i for a in ["ramanshift", "clean_spectrum"])
        ]
        self.register_df.plot(x="ramanshift", y=_raw_lbls)
