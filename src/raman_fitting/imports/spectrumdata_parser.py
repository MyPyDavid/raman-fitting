"""
Created on Mon Jul  5 21:09:06 2021

@author: DW
"""

from dataclasses import dataclass, field
import hashlib

from pathlib import Path
from functools import partial

from typing import Callable

from tablib import Dataset

from .spectrum.validators import ValidateSpectrumValues
from .files.validators import validate_filepath
from .spectrum import SPECTRUM_FILETYPE_PARSERS

from raman_fitting.models.spectrum import SpectrumData

from loguru import logger


spectrum_data_keys = ("ramanshift", "intensity")

ramanshift_expected_values = ValidateSpectrumValues(
    spectrum_key="ramanshift", min=-95, max=3650, len=1600
)
intensity_expected_values = ValidateSpectrumValues(
    spectrum_key="intensity", min=0, max=1e4, len=1600
)

spectrum_keys_expected_values = {
    "ramanshift": ramanshift_expected_values,
    "intensity": intensity_expected_values,
}


def get_file_parser(filepath: Path) -> Callable[[Path], Dataset]:
    "Get callable file parser function."
    suffix = filepath.suffix
    parser = SPECTRUM_FILETYPE_PARSERS[suffix]["method"]
    kwargs = SPECTRUM_FILETYPE_PARSERS[suffix].get("kwargs", {})
    return partial(parser, **kwargs)


@dataclass
class SpectrumReader:
    """
    Reads a spectrum from a 'raw' data file Path or str

    with spectrum_data_keys "ramanshift" and "intensity".
    Double checks the values
    Sets a hash attribute afterwards
    """

    filepath: Path | str
    spectrum_data_keys: tuple = field(default=spectrum_data_keys, repr=False)

    spectrum: SpectrumData = field(default=None)
    label: str = "raw"
    region_name: str = "full"
    spectrum_hash: str = field(default=None, repr=False)
    spectrum_length: int = field(default=0, init=False)

    def __post_init__(self):
        super().__init__()

        self.filepath = validate_filepath(self.filepath)
        self.spectrum_length = 0

        if self.filepath is None:
            raise ValueError(f"File is not valid. {self.filepath}")
        parser = get_file_parser(self.filepath)
        parsed_spectrum = parser(self.filepath, self.spectrum_data_keys)
        if parsed_spectrum is None:
            return
        for spectrum_key in parsed_spectrum.headers:
            if spectrum_key not in spectrum_keys_expected_values:
                continue
            validator = spectrum_keys_expected_values[spectrum_key]
            valid = validator.validate(parsed_spectrum)
            if not valid:
                logger.warning(
                    f"The values of {spectrum_key} of this spectrum are invalid. {validator}"
                )
        spec_init = {
            "label": self.label,
            "region_name": self.region_name,
            "source": self.filepath,
        }
        _parsed_spec_dict = {
            k: parsed_spectrum[k] for k in spectrum_keys_expected_values.keys()
        }
        spec_init.update(_parsed_spec_dict)
        self.spectrum = SpectrumData(**spec_init)

        self.spectrum_hash = self.get_hash_text(self.spectrum)
        self.spectrum_length = len(self.spectrum)

    @staticmethod
    def get_hash_text(data, hash_text_encoding="utf-8"):
        text = str(data)
        text_hash = hashlib.sha256(text.encode(hash_text_encoding)).hexdigest()
        return text_hash

    def __repr__(self):
        _txt = f"Spectrum({self.filepath.name}, len={self.spectrum_length})"
        return _txt

    def quickplot(self):
        """Plot for quickly checking the spectrum"""
        try:
            self.spectrum.plot(x="ramanshift", y="intensity")
        except TypeError:
            logger.warning("No numeric data to plot")
