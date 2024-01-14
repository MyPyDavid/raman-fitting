import hashlib
from pathlib import Path
from typing import Optional, Dict, List

from pydantic import (
    BaseModel,
    FilePath,
    model_validator,
    Field,
    ConfigDict,
    NewPath,
)

from .samples.sample_id_helpers import (
    parse_string_to_sample_id_and_position,
    sID_to_sgrpID,
)
from .samples.sample_id_helpers import (
    overwrite_sID_from_mapper,
    overwrite_sgrpID_from_parts,
)
from .files.metadata import FileMetaData, get_file_metadata
from .samples.models import SampleMetaData

# index_primary_key = "rfID"
# index_file_primary_keys = {f"{index_primary_key}": "string"}
# index_file_path_keys = {"FileStem": "string", "FilePath": "Path"}
# index_file_sample_keys = {
#     "SampleID": "string",
#     "SamplePos": "int64",
#     "SampleGroup": "string",
# }

# index_file_read_text_keys = {"FileHash": "string", "FileText": "string"}

# index_dtypes_collection = {
#     **index_file_path_keys,
#     **index_file_sample_keys,
#     **index_file_stat_keys,
#     **index_file_read_text_keys,
# }


# index_file_stat_keys = {
#     "FileCreationDate": "datetime64",
#     "FileCreation": "float",
#     "FileModDate": "datetime64",
#     "FileMod": "float",
#     "FileSize": "int64",
# }


class RamanFileInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: FilePath
    filename_id: str = Field(None, init_var=False, validate_default=False)
    sample: SampleMetaData = Field(None, init_var=False, validate_default=False)
    file_metadata: FileMetaData = Field(None, init_var=False, validate_default=False)
    export_dir: NewPath = Field(None, init_var=False, validate_default=False)

    @model_validator(mode="after")
    def set_filename_id(self) -> "RamanFileInfo":
        filename_id = get_filename_id_from_path(self.file)
        self.filename_id = filename_id
        return self

    @model_validator(mode="after")
    def parse_and_set_sample_from_file(self) -> "RamanFileInfo":
        sample = parse_sample_from_filepath(self.file)
        self.sample = sample
        return self

    @model_validator(mode="after")
    def parse_and_set_metadata_from_filepath(self) -> "RamanFileInfo":
        file_metadata = get_file_metadata(self.file)
        self.file_metadata = FileMetaData(**file_metadata)
        return self


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
    fnID = f"{_parent_suffix_hash}_{path.stem}"
    return fnID


def extra_assign_export_dir_on_index(result_dir, index: List[RamanFileInfo]):
    """assign the DestDir column to index and sets column values as object type"""
    _index = []

    for rf_info in index:
        rf_info.export_dir = result_dir.joinpath(rf_info.sample.group)
        _index.append(rf_info)
    return _index


def parse_sample_from_filepath(
    filepath: Path, sample_name_mapper: Optional[Dict[str, Dict[str, str]]] = None
) -> SampleMetaData:
    """parse the sID, position and sgrpID from stem"""
    stem = filepath.stem
    parts = filepath.parts

    sID, position = parse_string_to_sample_id_and_position(stem)

    if sample_name_mapper is not None:
        sample_id_mapper = sample_name_mapper.get("sample_id", {})
        sID = overwrite_sID_from_mapper(sID, sample_id_mapper)
    sgrpID = sID_to_sgrpID(sID)

    if sample_name_mapper is not None:
        sample_grp_mapper = sample_name_mapper.get("sample_group_id", {})
        sgrpID = overwrite_sgrpID_from_parts(parts, sgrpID, sample_grp_mapper)

    sample = SampleMetaData(**{"id": sID, "group": sgrpID, "position": position})
    return sample
