from pathlib import Path
from typing import Dict
from datetime import date
import datetime
from typing import Any


from pydantic import (
    BaseModel,
    FilePath,
    PastDatetime,
)


class FileMetaData(BaseModel):
    file: FilePath
    creation_date: date
    creation_datetime: PastDatetime
    modification_date: date
    modification_datetime: PastDatetime
    size: int


def get_file_metadata(filepath: Path) -> Dict[str, Any]:
    """converting creation time and last mod time to datetime object"""
    fstat = filepath.stat()
    c_t = fstat.st_ctime
    m_t = fstat.st_mtime
    c_tdate, m_tdate = c_t, m_t

    try:
        c_t = datetime.datetime.fromtimestamp(fstat.st_ctime)
        m_t = datetime.datetime.fromtimestamp(fstat.st_mtime)
        c_tdate = c_t.date()
        m_tdate = m_t.date()
    except OverflowError:
        pass
    except OSError:
        pass
    ret = {
        "file": filepath,
        "creation_date": c_tdate,
        "creation_datetime": c_t,
        "modification_date": m_tdate,
        "modification_datetime": m_t,
        "size": fstat.st_size,
    }
    return ret
