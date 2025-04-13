from black.ranges import Sequence
from pydantic import BaseModel, FilePath, ConfigDict, computed_field, Field

from raman_fitting.imports.samples.sample_id_helpers import (
    extract_sample_metadata_from_filepath,
)

from raman_fitting.imports.files.metadata import FileMetaData, get_file_metadata
from raman_fitting.imports.files.utils import get_filename_id_from_path
from raman_fitting.imports.samples.models import SampleMetaData

from tablib import Dataset
from tablib.exceptions import InvalidDimensions
from loguru import logger


class RamanFileInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: FilePath

    @computed_field
    @property
    def filename_id(self) -> str:
        return get_filename_id_from_path(self.file)

    @computed_field
    @property
    def sample(self) -> SampleMetaData:
        return extract_sample_metadata_from_filepath(self.file)

    @computed_field
    @property
    def file_metadata(self) -> FileMetaData:
        return FileMetaData(**get_file_metadata(self.file))


class RamanFileInfoSet(BaseModel):
    raman_files: Sequence[RamanFileInfo] = Field(default_factory=list)

    @classmethod
    def from_dataset(cls, dataset: Dataset) -> "RamanFileInfoSet":
        raman_files = []
        for row in dataset:
            row_data = dict(zip(dataset.headers, row))
            raman_files.append(RamanFileInfo(**row_data))
        return cls(raman_files=raman_files)

    def __len__(self) -> int:
        return len(self.raman_files)

    def __getitem__(self, index: int) -> RamanFileInfo:
        return self.raman_files[index]

    def __iter__(self):
        return iter(self.raman_files)

    def cast_to_dataset(self) -> Dataset | None:
        headers = list(RamanFileInfo.model_fields.keys()) + list(
            RamanFileInfo.model_computed_fields.keys()
        )
        data = Dataset(headers=headers)
        for file in self.raman_files:
            try:
                data.append(file.model_dump(mode="json").values())
            except InvalidDimensions as e:
                logger.error(f"Error adding file to dataset: {e}")
        if len(data) == 0:
            logger.error(
                f"No data was added to the dataset for {len(self.raman_files)} files."
            )
            return None
        return data
