import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def validate_filepath(filepath: Path, max_bytesize=10**6):
    if not (isinstance(filepath, Path) or isinstance(filepath, str)):
        raise TypeError("Argument given is not Path nor str")

    filepath = Path(filepath)

    if not filepath.exists():
        logger.warning("File does not exist")
        return

    filesize = filepath.stat().st_size
    if filesize > max_bytesize:
        logger.warning(f"File too large ({filesize})=> skipped")
        return
    return filepath
