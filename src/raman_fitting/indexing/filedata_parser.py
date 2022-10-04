"""
Created on Mon Jul  5 21:09:06 2021

@author: DW
"""
import hashlib
import logging
from pathlib import Path
from warnings import warn

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


#%%
class SpectrumReader:
    """
    Reads a clean spectrum from a file Path or str

    with columns "ramanshift" and "intensity".
    Double checks the values
    Sets a hash attribute afterwards
    """

    supported_filetypes = [".txt"]

    spectrum_data_keys = ("ramanshift", "intensity")
    spectrum_keys_expected_values = {
        "ramanshift": {"expected_values": {"min": -95, "max": 3600, "len": 1600}},
        "intensity": {"expected_values": {"min": 0, "max": 1e4, "len": 1600}},
    }
    # expected_ranges = {"ramanshift": (-95, 3600)}
    # expected_length = 1600
    # using slots since there will be many instances of this class

    __slots__ = (
        *("filepath", "max_bytesize", "spectrum", "spectrum_hash", "spectrum_length"),
        *spectrum_keys_expected_values.keys(),
    )

    def __init__(self, filepath: Path, max_bytesize=10 ** 6):

        if not isinstance(filepath, Path):
            if isinstance(filepath, str):
                filepath = Path(filepath)
            else:
                raise TypeError("Argument given is not Path nor str")

        self.filepath = filepath
        self.max_bytesize = max_bytesize

        self.spectrum = pd.DataFrame(data=[], columns=self.spectrum_data_keys)
        if filepath.exists():
            filesize = filepath.stat().st_size
            if filesize < max_bytesize:

                self.spectrum = self.spectrum_parser(self.filepath)
                self.double_check_spectrum_values(
                    self.spectrum, expected_values=self.spectrum_keys_expected_values
                )
        else:
            logger.warning("File does not exist")

        self.spectrum_hash = self.get_hash_text(self.spectrum)
        self.spectrum_length = len(self.spectrum)

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

        suffix = ""
        suffix = filepath.suffix
        if suffix in self.supported_filetypes:
            if suffix == ".txt":

                try:
                    spectrum_data = self.use_np_loadtxt(filepath)

                except Exception as exc:
                    logger.warning(
                        f"Can not complete use_np_loadtxt for:\n{filepath}\n{exc}"
                    )
                    # data = self.read_text(self.filepath)
            elif suffix == ".xlsx":
                # read excel file input
                # IDEA not implemented yet, select columns etc or autodetect
                spectrum_data = pd.read_excel(filepath)

            elif suffix == ".csv":
                # read csv file input
                # IDEA not implemented yet, select columns etc or autodetect
                spectrum_data = pd.read_excel(filepath)

        else:
            logger.warning(f"Filetype {suffix} not supported")

        return spectrum_data

    def use_np_loadtxt(self, filepath, usecols=(0, 1), **kwargs):

        try:
            loaded_array = np.loadtxt(filepath, usecols=usecols, **kwargs)
        except IndexError:
            logger.debug(f"IndexError called np genfromtxt for {filepath}")
            loaded_array = np.genfromtxt(filepath, invalid_raise=False)
        except ValueError:
            logger.debug(f"ValueError called np genfromtxt for {filepath}")
            loaded_array = np.genfromtxt(filepath, invalid_raise=False)
        except Exception as exc:
            logger.warning(f"Can not load data from txt file: {filepath}\n{exc}")
            loaded_array = np.array([])

        spectrum_data = pd.DataFrame()
        if loaded_array.ndim == len(self.spectrum_data_keys):
            try:
                spectrum_data = pd.DataFrame(
                    loaded_array, columns=self.spectrum_data_keys
                )
            except Exception as exc:
                logger.warning(
                    f"Can not create DataFrame from array object: {loaded_array}\n{exc}"
                )
        return spectrum_data

    def double_check_spectrum_values(
        self, spectrum_data: pd.DataFrame, expected_values: dict = {}
    ):
        if all([i in spectrum_data.columns for i in expected_values.keys()]):
            _len = len(spectrum_data)
            for _key, expectations in expected_values.items():

                if expectations:
                    for exp_method, exp_value in expectations.items():
                        _check = False
                        if "len" in exp_method:
                            _spectrum_value = _len
                            _check = np.isclose(_spectrum_value, exp_value, rtol=0.1)

                        elif "min" in exp_method:
                            _spectrum_value = spectrum_data[_key].min()
                            _check = np.isclose(_spectrum_value, exp_value, rtol=0.2)
                            if not _check:
                                _check = exp_value >= _spectrum_value
                        elif "max" in exp_method:
                            _spectrum_value = spectrum_data[_key].max()
                            _check = exp_value <= _spectrum_value
                        else:
                            # not implemented
                            _check = True
                        if not _check:
                            logger.warning(
                                f"The {exp_method} of this spectrum ({_spectrum_value }) does not match the expected values {exp_value}"
                            )
        else:
            logger.error(
                f"The dataframe does not have all the keys from {self.spectrum_data_keys}"
            )

    @staticmethod
    def read_text(filepath, max_bytes=10 ** 6, encoding="utf-8", errors=None):
        """additional read text method for raw text data inspection"""
        _text = "read_text_method"
        filesize = filepath.stat().st_size
        if filesize < max_bytes:
            try:
                _text = filepath.read_text(encoding=encoding, errors=errors)
                # _text.splitlines()
            except Exception as exc:
                # IDEA specify which Exceptions are expected
                _text += "\nread_error"
                logger.warning(f"file read text error => skipped.\n{exc}")
        else:
            _text += "\nfile_too_large"
            logger.warning(f" file too large ({filesize})=> skipped")

        return _text

    def load_data(self, filepath):
        """old method taken out from SpectrumConstructor"""
        # on_lbl="raw"
        # assert self.file.exists(), f'File: "{self.file}" does not exist.'
        # IDEA import file reader class here
        ramanshift, intensity = np.array([]), np.array([])
        i = 0
        while not ramanshift.any() and i < 2000:
            try:
                ramanshift, intensity = np.loadtxt(
                    filepath, usecols=(0, 1), delimiter="\t", unpack=True, skiprows=i
                )
                # Alternative parsing method with pandas.read_csv
                # _rawdf = pd.read_csv(self.file, usecols=(0, 1), delimiter='\t',
                #                     skiprows=i, header =None, names=['ramanshift','intensity'])
                logger.info(
                    f"{self.file} with len rs({len(ramanshift)}) and len int({len(intensity)})"
                )
                # self._read_succes = True
                # self.spectrum_length = len(ramanshift)
                # self.info.update(
                # {"spectrum_length": self.spectrum_length, "skipped_rows": i})
            except ValueError:
                i += 1

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
            logger.warning(f"No numeric data to plot")
