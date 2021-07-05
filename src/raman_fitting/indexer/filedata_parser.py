"""
Created on Mon Jul  5 21:09:06 2021

@author: DW
"""
from warnings import warn
from pathlib import Path
import hashlib

class DataParser:
    '''
    Possible class to read in data from differnt file types
    before a Spectrum is constructed from the data.
    Not in use since text is directly loaded into Spectrum in
    the SpectrumConstructor
    # TODO Add conversion into DataFrame
    '''

    supported_types = ['.txt']


    def __init__(self, filepath: Path):
        self.filepath = filepath


    def data_parser(self):
        if self.filepath.exists():
            _suffix = self.filepath.suffix
            if _suffix in self.support_types:
                if _suffix == '.txt':
                    _rawdata, _rawdatahash = self.read_text(self.filepath)
            else:
                warn('Filetype not supported')

        else:
            warn('File does not exist')

    def read_text(filepath, max_bytes=10 ** 6):
        """read text introspection into files, might move this to a higher level"""
        _text = ""
        if filepath.stat().st_size < max_bytes:
            try:
                _text = filepath.read_text(encoding="utf-8")
            except Exception as e:
                _text - "read_error"
                logger.warning(f"{self._qcnm} file read text error => skipped.\n{e}")
        else:
            _text = "max_size"
            logger.warning(f"{self._qcnm} file too large => skipped")
        filehash = hashlib.md5(_text.encode("utf-8")).hexdigest()
        return _text, filehash
