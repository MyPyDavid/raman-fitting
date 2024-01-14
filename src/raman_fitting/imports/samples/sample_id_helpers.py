from typing import List, Tuple


def parse_string_to_sample_id_and_position(
    string: str, seps=("_", " ", "-")
) -> Tuple[str, str]:
    """
    Parser for the filenames -> finds SampleID and sample position

    Parameters
    ----------
    # ramanfile_string : str
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
        [n for n, i in enumerate(seps) if i in string], default=None
    )
    first_sep_match = (
        seps[first_sep_match_index] if first_sep_match_index is not None else None
    )
    split = string.split(first_sep_match)
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
    return (sID, position)


def sID_to_sgrpID(sID: str, max_len=4) -> str:
    """adding the extra sample Group key from sample ID"""

    _len = len(sID)
    _maxalphakey = min(
        [n for n, i in enumerate(sID) if not str(i).isalpha()], default=_len
    )
    _maxkey = min((_len, _maxalphakey, max_len))
    sgrpID = "".join([i for i in sID[0:_maxkey] if i.isalpha()])
    return sgrpID


def overwrite_sID_from_mapper(sID: str, mapper: dict) -> str:
    """Takes an sID and potentially overwrites from a mapper dict"""
    _sID_map = mapper.get(sID, None)
    if _sID_map:
        sID = _sID_map
    return sID


def overwrite_sgrpID_from_parts(parts: List[str], sgrpID: str, mapper: dict) -> str:
    for k, val in mapper.items():
        if k in parts:
            sgrpID = val
    return sgrpID
