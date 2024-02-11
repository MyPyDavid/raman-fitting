from pydantic import (
    BaseModel,
    FilePath,
    model_validator,
    Field,
    ConfigDict,
)

from .samples.sample_id_helpers import parse_sample_from_filepath

from .files.metadata import FileMetaData, get_file_metadata
from .files.index_helpers import get_filename_id_from_path
from .samples.models import SampleMetaData


class RamanFileInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: FilePath
    filename_id: str = Field(None, init_var=False, validate_default=False)
    sample: SampleMetaData = Field(None, init_var=False, validate_default=False)
    file_metadata: FileMetaData = Field(None, init_var=False, validate_default=False)

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


# def extra_assign_export_dir_on_index(result_dir, index: List[RamanFileInfo]):
#     """assign the DestDir column to index and sets column values as object type"""
#     _index = []

#     for rf_info in index:
#         rf_info.export_dir = result_dir.joinpath(rf_info.sample.group)
#         _index.append(rf_info)
#     return _index
