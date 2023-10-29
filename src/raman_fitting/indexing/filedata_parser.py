"""
Created on Mon Jul  5 21:09:06 2021

@author: DW
"""
from dataclasses import dataclass, field
import hashlib
import logging
from pathlib import Path
import re

from warnings import warn
from typing import List

import numpy as np
import pandas as pd

from .file_parsers import load_spectrum_from_txt
from .validators import ValidateSpectrumValues

logger = logging.getLogger(__name__)


SPECTRUM_FILETYPE_PARSERS = {
        ".txt": { 
            "method": load_spectrum_from_txt,
            "kwargs": {
                "usecols": (0, 1),
                "keys": ("ramanshift", "intensity"),
                },
        },
        ".xlsx": {
            "method": pd.read_excel,
            "kwargs": {},
        },
        ".csv": {
            "method": pd.read_csv,
            "kwargs": {},
        },
}

supported_filetypes = [".txt"]
spectrum_data_keys = ("ramanshift", "intensity")

ramanshift_expected_values = ValidateSpectrumValues(spectrum_key="ramanshift", min=-95, max=3600, len=1600)
intensity_expected_values = ValidateSpectrumValues(spectrum_key="intensity", min=0, max=1e4, len=1600)


@dataclass
class SpectrumReader:
    """
    Reads a clean spectrum from a file Path or str

    with columns "ramanshift" and "intensity".
    Double checks the values
    Sets a hash attribute afterwards
    """
    filepath: Path | str
    max_bytesize: int = 10**6
    spectrum_data_keys: tuple = ("ramanshift", "intensity")
    spectrum_keys_expected_values: List[ValidateSpectrumValues] = field(default_factory=list)
    spectrum: pd.DataFrame = field(default_factory=pd.DataFrame)
    spectrum_hash: str = ""
    spectrum_length: int = 0


    def __post_init__(self, **kwargs):
        super().__init__()

        if not (isinstance(self.filepath, Path) or isinstance(self.filepath, str)):
            raise TypeError("Argument given is not Path nor str")

        self.filepath = Path(self.filepath)
        self.spectrum_length = 0
        for key in self.spectrum_data_keys:
            setattr(self, key, np.array([]))

        self.spectrum = pd.DataFrame(data=[], columns=self.spectrum_data_keys)
        if not self.filepath.exists():
            logger.warning("File does not exist")
            return

        filesize = self.filepath.stat().st_size
        if filesize > self.max_bytesize:
            logger.warning(f"File too large ({filesize})=> skipped")
            return

        self.spectrum = self.spectrum_parser(self.filepath)
        for spectrum_key in self.spectrum.columns:
            validators = list(filter(lambda x: x.spectrum_key == spectrum_key, self.spectrum_keys_expected_values))
            for validator in validators:
                self.validate_spectrum_keys_expected_values(self.spectrum, validator)

        self.spectrum_hash = self.get_hash_text(self.spectrum)
        self.spectrum_length = len(self.spectrum)

        # sort spectrum data by ramanshift
        self.spectrum = self.sort_spectrum(
            self.spectrum, sort_by="ramanshift", ignore_index=True
        )

        for key in self.spectrum_data_keys:
            setattr(self, key, self.spectrum[key].to_numpy())

    def spectrum_parser(self, filepath: Path):
        """
        Reads data from a file and converts into pd.DataFrame object

        Parameters
        --------
        filepath : Path, str
            file which contains the data of a spectrum

        Returns
        --------
        pd.DataFrame
            Contains the data of the spectrum in a DataFrame with the selected spectrum keys as columns
        """

        spectrum_data = pd.DataFrame()

        suffix = filepath.suffix

        if suffix not in SPECTRUM_FILETYPE_PARSERS:
            raise ValueError(f"Filetype {suffix} not supported")
        
        parser = SPECTRUM_FILETYPE_PARSERS[suffix]["method"]
        kwargs = SPECTRUM_FILETYPE_PARSERS[suffix]["kwargs"]
        spectrum_data = parser(filepath, **kwargs)

        return spectrum_data


    def validate_spectrum_keys_expected_values(
        self, spectrum_data: pd.DataFrame, expected_values: ValidateSpectrumValues
    ):
        if not expected_values.spectrum_key not in spectrum_data.columns:
            logger.error(
                f"The expected value type {expected_values.spectrum_key} is not in the columns {spectrum_data.columns}"
            )
        if spectrum_data.empty:
            logger.error("Spectrum data is empty")
            return

        validation = expected_values.validate_spectrum(spectrum_data)
  
        if not validation:
            logger.warning(
                f"The {expected_values.spectrum_key} of this spectrum does not match the expected values {expected_values}"
            )


   
    def sort_spectrum(
        self, spectrum: pd.DataFrame, sort_by="ramanshift", ignore_index=True
    ):
        """sort the spectrum by the given column"""
        if sort_by in spectrum.columns:
            spectrum = spectrum.sort_values(by=sort_by, ignore_index=ignore_index)
        else:
            logger.warning(f"sort_by column {sort_by} not in spectrum")
        return spectrum

    @staticmethod
    def get_hash_text(dataframe, hash_text_encoding="utf-8"):
        text = dataframe.to_string()
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

