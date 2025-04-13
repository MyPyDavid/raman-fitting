import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_filepath(filepath: Path, max_bytesize=10**6) -> Path:
    """
    Validate the filepath and check if the file exists and is not too large.
    """

    if not isinstance(filepath, (Path, str)):
        raise TypeError("Argument given is not Path nor str")

    filepath = Path(filepath).resolve()

    if not filepath.exists():
        raise FileNotFoundError("File does not exist")

    filesize = filepath.stat().st_size
    if filesize > max_bytesize:
        raise ValueError(f"File too large ({filesize})=> skipped")
    return filepath
