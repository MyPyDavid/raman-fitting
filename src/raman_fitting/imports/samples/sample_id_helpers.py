from typing import Tuple, Optional, Dict
from pathlib import Path

from .models import SampleMetaData


def parse_string_to_sample_id_and_position(
    string: str, seps=("_", " ", "-")
) -> Tuple[str, int]:
    """
    Parser for the filenames -> finds SampleID and sample position.

    Parameters
    ----------
    string : str
        The filepath which is parsed.
    seps : tuple of str, default ('_', ' ', '-')
        Ordered collection of separators tried for split.

    Returns
    -------
    tuple of (str, int)
        A tuple containing the sample ID and position.
    """
    first_sep = find_first_separator(string, seps)
    if first_sep is None:
        return string, 0

    split = string.split(first_sep)
    return extract_sample_id_and_position(split)


def find_first_separator(string: str, seps: tuple[str, ...]) -> str | None:
    """Find the first separator in the string from the given separators."""
    for sep in seps:
        if sep in string:
            return sep
    return None


def extract_position(position_str: str) -> int:
    """Extract the position as an integer from the string."""
    digits = "".join(filter(str.isdigit, position_str))
    if digits:
        try:
            return int(digits)
        except ValueError:
            pass
    return 0


def extract_sample_id_and_position(split: list) -> tuple[str, int]:
    """Extract the sample ID and position from the split string."""
    sample_id = ""
    position = 0

    if len(split) == 1:
        sample_id = split[0]
    elif len(split) == 2:
        sample_id = split[0]
        position = extract_position(split[1])
    elif len(split) >= 3:
        sample_id = "_".join(split[:-1])
        position = extract_position(split[-1])

    return sample_id, position


def extract_sample_group_from_sample_id(sample_id: str, max_len=4) -> str:
    """adding the extra sample Group key from sample ID"""

    _len = len(sample_id)
    _maxalphakey = min(
        [n for n, i in enumerate(sample_id) if not str(i).isalpha()], default=_len
    )
    _maxkey = min((_len, _maxalphakey, max_len))
    sample_group_id = "".join([i for i in sample_id[0:_maxkey] if i.isalpha()])
    return sample_group_id


def overwrite_sample_id_from_mapper(sample_id: str, mapper: dict) -> str:
    """Takes an sample_id and potentially overwrites from a mapper dict"""
    sample_id_map = mapper.get(sample_id)
    if sample_id_map is not None:
        return sample_id_map
    return sample_id


def overwrite_sample_group_id_from_parts(
    parts: list[str] | tuple[str, ...], sample_group_id: str, mapper: dict
) -> str:
    for k, val in mapper.items():
        if k in parts:
            sample_group_id = val
    return sample_group_id


def extract_sample_metadata_from_filepath(
    filepath: Path, sample_name_mapper: Optional[Dict[str, Dict[str, str]]] = None
) -> SampleMetaData:
    """parse the sample_id, position and sgrpID from stem"""
    stem = filepath.stem
    parts = filepath.parts

    sample_id, position = parse_string_to_sample_id_and_position(stem)

    if sample_name_mapper is not None:
        sample_id_mapper = sample_name_mapper.get("sample_id", {})
        sample_id = overwrite_sample_id_from_mapper(sample_id, sample_id_mapper)
    sample_group_id = extract_sample_group_from_sample_id(sample_id)

    if sample_name_mapper is not None:
        sample_grp_mapper = sample_name_mapper.get("sample_group_id", {})
        sample_group_id = overwrite_sample_group_id_from_parts(
            parts, sample_group_id, sample_grp_mapper
        )

    return SampleMetaData(id=sample_id, group=sample_group_id, position=position)
