import datetime
import hashlib
import logging
from pathlib import Path

from .. import __package_name__
from .filedata_parser import DataParser

logger = logging.getLogger(__package_name__)

#%%


class PathParser(Path):

    _flavour = type(Path())._flavour

    _extra_sID_name_mapper = {
        "David": "DW",
        "stephen": "SP",
        "Alish": "AS",
        "Aish": "AS",
    }
    _extra_sgrpID_name_mapper = {"Raman Data for fitting David": "SH"}

    # _extra_sID_name = 'Si-ref'

    index_file_path_keys = {"FileStem": "string", "FilePath": "Path"}
    index_file_sample_keys = {
        "SampleID": "string",
        "SamplePos": "int64",
        "SampleGroup": "string",
    }
    index_file_stat_keys = {
        "FileCreationDate": "datetime64",
        "FileCreation": "float",
        "FileModDate": "datetime64",
        "FileMod": "float",
        "FileSize": "int64",
    }
    index_file_read_text_keys = {"FileHash": "string", "FileText": "string"}
    index_dtypes = {
        **index_file_path_keys,
        **index_file_sample_keys,
        **index_file_stat_keys,
        **index_file_read_text_keys,
    }

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._qcnm = self.__class__.__qualname__
        self.stats_ = None
        self.data = None
        self.parse_result = self.collect_parse_results(**kwargs)

    def collect_parse_results(self, read_data=False):
        """performs all the steps for parsing the filepath"""
        parse_res_collect = {}
        if self.exists():
            if self.is_file():
                self.stats_ = self.stat()
                _filepath = self.make_dict_from_keys(
                    "index_file_path_keys", (self.stem, self)
                )
                _sample = self.parse_sample_with_checks()
                _filestats = self.parse_filestats(self.stats_)
                if read_data == True:
                    self.data = DataParser(self)

                parse_res_collect = {**_filepath, **_sample, **_filestats}
            else:
                logger.warning(f"{self._qcnm} {self} is not a file => skipped")
        else:
            logger.warning(f"{self._qcnm} {self} does not exist => skipped")
        return parse_res_collect

    def parse_sample_with_checks(self):
        """parse the sID, position and sgrpID from stem"""
        # _parse_res  = ()
        # _parse_res = self._extra_sID_check_if_reference()
        _parse_res = ParserMethods.parse_filestem_to_sid_and_pos(self.stem)
        if len(_parse_res) == 2:
            sID, position = _parse_res
            sID = self._extra_sID_overwrite_from_mapper_attr(sID)
            sgrpID = ParserMethods.parse_sID_to_sgrpID(sID)
            sgrpID = self._extra_sgrID_overwrite_from_parts(
                sgrpID, mapper=self._extra_sgrpID_name_mapper
            )
            _parse_res = sID, position, sgrpID
        return self.make_dict_from_keys("index_file_sample_keys", _parse_res)

    def _extra_sgrID_overwrite_from_parts(self, sgrpID: str, mapper: dict = {}):
        if hasattr(self, "parts"):
            for k, val in mapper.items():
                if k in self.parts:
                    sgrpID = val
        return sgrpID

    def _extra_sID_overwrite_from_mapper_attr(
        self, sID: str, mapper_attr: str = "_extra_sID_name_mapper"
    ):
        """Takes an sID and potentially overwrites from a mapper dict"""
        if hasattr(self, mapper_attr):
            get_map_attr = getattr(self, mapper_attr)
            if isinstance(get_map_attr, dict):
                _sID_map = get_map_attr.get(sID, None)
                if _sID_map:
                    sID = _sID_map
        return sID

    def parse_filestats(self, fstat):
        """get status metadata from a file"""
        # fstat = self.stats_
        filestat_out = ParserMethods.parse_fstats(fstat)
        return self.make_dict_from_keys("index_file_stat_keys", filestat_out)
        # if len(self.index_file_stat_keys) == len(filestat_out):
        #     filestat_out =  dict(zip(self.index_file_stat_keys, filestat_out))
        # return filestat_out

    def make_dict_from_keys(self, _keys_attr: str, _result: tuple):
        """returns dict from tuples of keys and results"""
        _keys = ()
        if hasattr(self, _keys_attr):
            _keys = getattr(self, _keys_attr)
        if not len(_result) == len(_keys):
            # if len not matches make stand in numbered keys
            _keys = [f"{_keys_attr}_{n}" for n, i in enumerate(_result)]
        return dict(zip(_keys, _result))


class ParserMethods:
    """Collection of method for parsing a filename"""

    @staticmethod
    def parse_filestem_to_sid_and_pos(stem: str, seps=("_", " ", "-")):
        """
        Parser for the filenames -> finds SampleID and sample position

        Parameters
        ----------
        # ramanfile_stem : str
        #    The filepath which the is parsed
        seps : tuple of str default
            ordered collection of seperators tried for split
            default : ('_', ' ', '-')

        Returns
        -------
        tuple of strings
            Collection of strings which contains the parsed elements.
        """

        split = None
        first_sep_match_index = min(
            [n for n, i in enumerate(seps) if i in stem], default=None
        )
        first_sep_match = (
            seps[first_sep_match_index] if first_sep_match_index != None else None
        )
        split = stem.split(first_sep_match)
        _lensplit = len(split)

        if _lensplit == 0:
            sID, position = split[0], 0
        elif len(split) == 1:
            sID, position = split[0], 0
        elif len(split) == 2:
            sID = split[0]
            _pos_strnum = "".join(i for i in split[1] if i.isnumeric())
            if _pos_strnum:
                position = int(_pos_strnum)
            else:
                position = split[1]
        elif len(split) >= 3:
            sID = "_".join(split[0:-1])
            position = int("".join(filter(str.isdigit, split[-1])))
        #                split =[split_Nr0] + [position]
        return (sID, position)
        # else:
        #     sID = split[0] # default take split[0]
        #     if ''.join(((filter(str.isdigit,split[-1])))) == '':
        #         position = 0
        #     else:
        #         position = int(''.join(filter(str.isdigit,split[-1])))

    @staticmethod
    def parse_sID_to_sgrpID(sID: str, max_len=4):
        """adding the extra sample Group key from sample ID"""

        _len = len(sID)
        _maxalphakey = min(
            [n for n, i in enumerate(sID) if not str(i).isalpha()], default=_len
        )
        _maxkey = min((_len, _maxalphakey, max_len))
        sgrpID = "".join([i for i in sID[0:_maxkey] if i.isalpha()])
        return sgrpID

    @staticmethod
    def parse_fstats(fstat):
        """converting creation time and last mod time to datetime object"""
        c_t = fstat.st_ctime
        m_t = fstat.st_mtime
        c_tdate, m_tdate = c_t, m_t

        try:
            c_t = datetime.datetime.fromtimestamp(fstat.st_ctime)
            m_t = datetime.datetime.fromtimestamp(fstat.st_mtime)
            c_tdate = c_t.date()
            m_tdate = m_t.date()
        except OverflowError as e:
            pass
        except OSError as e:
            pass
        return c_tdate, c_t, m_tdate, m_t, fstat.st_size

    # def _extra_sID_check_if_reference(self, ref_ID = 'Si-ref'):
    #     if ref_ID in self.stem:
    #         position = 0
    #         sID = 'Si-ref'
    #         return (sID, position)
    #     else:
    #         return None
