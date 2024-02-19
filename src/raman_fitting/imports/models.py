import json
from pydantic import (
    BaseModel,
    FilePath,
    model_validator,
    Field,
    ConfigDict,
)

from .samples.sample_id_helpers import extract_sample_metadata_from_filepath

from .files.metadata import FileMetaData, get_file_metadata
from .files.index_helpers import get_filename_id_from_path
from .samples.models import SampleMetaData


class RamanFileInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: FilePath
    filename_id: str = Field(None, init_var=False, validate_default=False)
    sample: SampleMetaData | str = Field(None, init_var=False, validate_default=False)
    file_metadata: FileMetaData | str = Field(
        None, init_var=False, validate_default=False
    )

    @model_validator(mode="after")
    def set_filename_id(self) -> "RamanFileInfo":
        filename_id = get_filename_id_from_path(self.file)
        self.filename_id = filename_id
        return self

    @model_validator(mode="after")
    def parse_and_set_sample_from_file(self) -> "RamanFileInfo":
        sample = extract_sample_metadata_from_filepath(self.file)
        self.sample = sample
        return self

    @model_validator(mode="after")
    def parse_and_set_metadata_from_filepath(self) -> "RamanFileInfo":
        file_metadata = get_file_metadata(self.file)
        self.file_metadata = FileMetaData(**file_metadata)
        return self

    @model_validator(mode="after")
    def initialize_sample_and_file_from_dict(self) -> "RamanFileInfo":
        if isinstance(self.sample, dict):
            self.sample = SampleMetaData(**self.sample)
        elif isinstance(self.sample, str):
            _sample = json.loads(self.sample.replace("'", '"'))
            self.sample = SampleMetaData(**_sample)

        if isinstance(self.file_metadata, dict):
            self.file_metadata = FileMetaData(**self.file_metadata)
        elif isinstance(self.file_metadata, str):
            _file_metadata = json.loads(self.file_metadata.replace("'", '"'))
            self.file_metadata = SampleMetaData(**_file_metadata)

        return self
