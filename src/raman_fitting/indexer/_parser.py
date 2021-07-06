""" Parsing the contents of datafile of a spectrum into class instance """

from pathlib import Path

import numpy as np


class Parser:  # pragma: no cover
    """
    Parser class, handles the reading of datafiles
    """

    _supported_suffixes = [".txt"]

    def __init__(self, filepath):
        self.info = {}
        self._suffix = ""
        self.ramanshift = None
        self.intensity = None
        self._read_succes = False

        self.filepath = filepath

        self.choose_parsers()
        self.validate_data()

    @property
    def filepath(self):
        return self._filepath

    @filepath.setter
    def filepath(self, _fp):
        self.validate_fp(_fp)

    def validate_fp(self, _fp):
        _std_error_msg = f'Error in "{self.__class__.__name__}" with file:{_fp}\n'
        _errmsg = ""
        # TODO try typecasting into Path
        if _fp.__class__.__module__ != "pathlib":
            try:
                _fp = Path(_fp)
            except Exception as e:
                _errmsg = f"{_std_error_msg}-> can not be casted into path.\n{e}"
                raise ValueError(_errmsg)

        self._suffix = _fp.suffix

        if not _fp.is_file():
            _errmsg = f"{_std_error_msg}-> not a file."
            raise ValueError(_errmsg)

        if self._suffix not in self._supported_suffixes:
            _errmsg = f"""{_std_error_msg }-> Suffix "{self._suffix}" not in supported: {", ".join(self._supported_suffixes)}"""
            raise ValueError(_errmsg)
        self.info.update({"validate_error_msg": _errmsg})
        self._filepath = _fp

    def validate_data(self):
        if self._read_succes:
            if not all(self.ramanshift):
                pass

    def choose_parsers(self):
        if self._suffix == ".txt":
            self.parse_from_txt()

    def parse_from_txt(self, usecols=(0, 1), delimiter="\t", unpack=True, skiprows=0):
        ramanshift, intensity = np.array([]), np.array([])
        i = skiprows
        while not ramanshift.any() and i < 2000:
            try:
                ramanshift, intensity = np.loadtxt(
                    self.filepath,
                    usecols=usecols,
                    delimiter=delimiter,
                    unpack=unpack,
                    skiprows=i,
                )
                self.ramanshift = ramanshift
                self.intensity = intensity
                # Alternative parsing method with pandas.read_csv
                # _rawdf = pd.read_csv(self.file, usecols=(0, 1), delimiter='\t',
                #                     skiprows=i, header =None, names=['ramanshift','intensity'])
                # print(self.file, len(ramanshift), len(intensity))
                self._read_succes = True
                self.info.update(
                    {
                        "spectrum_length": len(ramanshift),
                        "_parser_skiprows": i,
                        "_parser_delimeter": delimiter,
                    }
                )
            except ValueError:
                i += 1
