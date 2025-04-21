from functools import partial
from pathlib import Path
from typing import Callable

from tablib import Dataset

from .reader import read_file_with_tablib
from .column_headers import get_default_expected_header_keys

SPECTRUM_FILETYPE_PARSERS = {
    ".txt": {
        "method": read_file_with_tablib,  # load_spectrum_from_txt,
    },
    ".xlsx": {
        "method": read_file_with_tablib,  # pd.read_excel,
    },
    ".csv": {
        "method": read_file_with_tablib,  # pd.read_csv,
    },
    ".json": {
        "method": read_file_with_tablib,
    },
}


def get_parser_method_for_filetype(
    filepath: Path, header_keys: tuple[str] | None = None, **kwargs
) -> Callable[[Path, dict], Dataset]:
    """Get callable file parser function."""
    parser = SPECTRUM_FILETYPE_PARSERS[filepath.suffix]["method"]
    parser_kwargs = SPECTRUM_FILETYPE_PARSERS[filepath.suffix].get("kwargs", {})
    kwargs.update(**parser_kwargs)
    if header_keys is None:
        header_keys = get_default_expected_header_keys()
    return partial(parser, header_keys=header_keys, **kwargs)
