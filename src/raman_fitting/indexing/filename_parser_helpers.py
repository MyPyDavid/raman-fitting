"""Collection of method for parsing a filename"""
# -*- coding: utf-8 -*-

import datetime
from typing import Tuple

# class ParserMethods

__all__ = ["filestem_to_sid_and_pos", "sID_to_sgrpID", "get_fstats"]


def filestem_to_sid_and_pos(stem: str, seps=("_", " ", "-")) -> Tuple[str, str]:
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
        seps[first_sep_match_index] if first_sep_match_index is not None else None
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


def sID_to_sgrpID(sID: str, max_len=4) -> str:
    """adding the extra sample Group key from sample ID"""

    _len = len(sID)
    _maxalphakey = min(
        [n for n, i in enumerate(sID) if not str(i).isalpha()], default=_len
    )
    _maxkey = min((_len, _maxalphakey, max_len))
    sgrpID = "".join([i for i in sID[0:_maxkey] if i.isalpha()])
    return sgrpID


def get_fstats(fstat) -> Tuple:
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
