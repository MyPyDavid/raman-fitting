"""
Created on Mon Jul  5 21:09:06 2021

@author: DW
"""
import hashlib
import logging
from pathlib import Path
from warnings import warn

from .. import __package_name__

logger = logging.getLogger(__package_name__)


#%%
class DataParser:
    """
    Possible class to read in data from differnt file types
    before a Spectrum is constructed from the data.
    Not in use since text is directly loaded into Spectrum in
    the SpectrumConstructor
    # TODO Add conversion into DataFrame
    """

    supported_filetypes = [".txt"]

    def __init__(self, filepath: Path):
        self.filepath = filepath

        self.data = self.data_parser(self.filepath)

    def data_parser(self, filepath):
        """Reads data from file and converts into array object"""

        _data = None
        _hash = None
        suffix = ""

        if filepath.exists():
            suffix = self.filepath.suffix

            if suffix in self.supported_filetypes:
                if suffix == ".txt":
                    _data = self.read_text(self.filepath)

                elif suffix == ".xlsx":
                    # read excel file input
                    pass
                elif suffix == ".csv":
                    # read csv file input
                    pass
            else:
                warn("Filetype not supported")

        else:
            warn("File does not exist")
        return _data, suffix

    def make_hash_from_data(self, data):
        _hash = self.get_hash_text(data)

    @staticmethod
    def read_text(filepath, max_bytes=10 ** 6, encoding="utf-8", errors=None):
        """read text introspection into files, might move this to a higher level"""
        _text = "read_text_method"
        filesize = filepath.stat().st_size
        if filesize < max_bytes:
            try:
                _text = filepath.read_text(encoding=encoding, errors=errors)
            except Exception as exc:
                # TODO specify which Exceptions are expected
                _text += "\nread_error"
                logger.warning(f"file read text error => skipped.\n{exc}")
        else:
            _text += "\nfile_too_large"
            logger.warning(f" file too large => skipped")

        return _text

    @staticmethod
    def get_hash_text(text, hash_text_encoding="utf-8"):
        filehash = hashlib.sha256(text.encode(hash_text_encoding)).hexdigest()
        return filehash
