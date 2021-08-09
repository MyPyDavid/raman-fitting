# import datetime
import hashlib
import logging
from pathlib import Path

from typing import Dict, List

# from .. import __package_name__

from .filedata_parser import SpectrumReader
from .filename_parser_helpers import filestem_to_sid_and_pos, sID_to_sgrpID, get_fstats

logger = logging.getLogger(__name__)

#%%
# _extra_sID_name = 'Si-ref'
index_primary_key = "rfID"
index_file_primary_keys = {f"{index_primary_key}": "string"}
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

index_dtypes_collection = {
    **index_file_path_keys,
    **index_file_sample_keys,
    **index_file_stat_keys,
    **index_file_read_text_keys,
}

# Extra name to sID mapper, if keys is in filename
_extra_sID_name_mapper = {
    "David": "DW",
    "stephen": "SP",
    "Alish": "AS",
    "Aish": "AS",
}

# Extra name to sID mapper, if key is in filepath parts
_extra_sgrpID_name_mapper = {"Raman Data for fitting David": "SH"}


def _extra_overwrite_sID_from_mapper(
    sID: str, mapper: dict = _extra_sID_name_mapper
) -> str:
    """Takes an sID and potentially overwrites from a mapper dict"""
    _sID_map = mapper.get(sID, None)
    if _sID_map:
        sID = _sID_map
    return sID


def _extra_overwrite_sgrpID_from_parts(
    parts: List[str], sgrpID: str, mapper: dict = _extra_sgrpID_name_mapper
) -> str:
    for k, val in _extra_sgrpID_name_mapper.items():
        if k in parts:
            sgrpID = val
    return sgrpID


class PathParser(Path):
    """
    This class parses the filepath of a file to a parse_result (dict),
    from which the main raman file index will be built up.

    """

    _flavour = type(Path())._flavour

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._qcnm = self.__class__.__qualname__
        self.stats_ = None
        self.data = None
        self.parse_result = self.collect_parse_results(**kwargs)

    @staticmethod
    def get_rfID_from_path(path: Path) -> str:
        """
        Makes the ID from a filepath

        Parameters
        ----------
        path : Path
            DESCRIPTION.

        Returns
        -------
        str: which contains hash(parent+suffix)_stem of path

        """

        _parent_suffix_hash = hashlib.sha512(
            (str(path.parent) + path.suffix).encode("utf-8")
        ).hexdigest()
        _filestem = path.stem
        fnID = _parent_suffix_hash + "_" + _filestem
        return fnID

    def collect_parse_results(
        self, read_data=False, store_data=False, **kwargs
    ) -> Dict:
        """performs all the steps for parsing the filepath"""
        parse_res_collect = {}

        if self.exists():
            if self.is_file():
                self.stats_ = self.stat()

                _fnID = self.make_dict_from_keys(
                    index_file_primary_keys, (self.get_rfID_from_path(self),)
                )
                _filepath = self.make_dict_from_keys(
                    index_file_path_keys, (self.stem, self)
                )
                _sample = self.parse_sample_with_checks()
                _filestats = self.parse_filestats(self.stats_)
                if read_data == True:
                    try:
                        self.data = SpectrumReader(self)
                    except Exception as exc:
                        logger.warning(
                            f"{self._qcnm} {self} SpectrumReader failed.\n{exc}"
                        )

                parse_res_collect = {**_fnID, **_filepath, **_sample, **_filestats}
            else:
                logger.warning(f"{self._qcnm} {self} is not a file => skipped")
        else:
            logger.warning(f"{self._qcnm} {self} does not exist => skipped")
        return parse_res_collect

    def parse_sample_with_checks(self):
        """parse the sID, position and sgrpID from stem"""

        _parse_res = filestem_to_sid_and_pos(self.stem)

        if len(_parse_res) == 2:
            sID, position = _parse_res

            try:
                sID = _extra_overwrite_sID_from_mapper(sID)
            except Exception as exc:
                logger.info(
                    f"{self._qcnm} {self} _extra_overwrite_sID_from_mapper failed => skipped.\n{exc}"
                )

            sgrpID = sID_to_sgrpID(sID)

            try:
                sgrpID = _extra_overwrite_sgrpID_from_parts(self.parts, sgrpID)
            except Exception as exc:
                logger.info(
                    f"{self._qcnm} {self} _extra_overwrite_sgrpID_from_parts failed => skipped.\n{exc}"
                )

            _parse_res = sID, position, sgrpID
        else:
            logger.warning(
                f"{self._qcnm} {self} failed to parse filename to sID and position."
            )
        return self.make_dict_from_keys(index_file_sample_keys, _parse_res)

    def parse_filestats(self, fstat) -> Dict:
        """get status metadata from a file"""

        filestats = get_fstats(fstat)
        return self.make_dict_from_keys(index_file_stat_keys, filestats)

    def make_dict_from_keys(self, _keys_attr: Dict, _result: tuple) -> Dict:
        """returns dict from tuples of keys and results"""
        if not isinstance(_result, tuple):
            logger.warning(
                f"{self._qcnm} input value is not a tuple, {_result}. Try to cast into tuple"
            )
            _result = (_result,)

        _keys = _keys_attr.keys()

        if not len(_result) == len(_keys) and not isinstance(_keys, str):
            # if len not matches make stand in numbered keys
            _keys = [f"{_keys_attr}_{n}" for n, i in enumerate(_result)]
        return dict(zip(_keys, _result))
