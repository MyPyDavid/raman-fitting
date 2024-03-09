import hashlib
from pathlib import Path


def get_filename_id_from_path(path: Path) -> str:
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
    filename_id = f"{_parent_suffix_hash}_{path.stem}"
    return filename_id
