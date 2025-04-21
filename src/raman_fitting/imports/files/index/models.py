from functools import cached_property

from raman_fitting.imports.files.index.validators import (
    validate_and_set_dataset,
    validate_index_file_path,
)
from raman_fitting.utils.writers import write_dataset_to_file
from raman_fitting.utils.loaders import load_dataset_from_file
from raman_fitting.imports.files.models import RamanFileInfoSet

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FilePath,
    NewPath,
    computed_field,
    PrivateAttr,
)

from loguru import logger
from tablib import Dataset


class RamanFileIndex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    index_file: NewPath | FilePath | None = Field(None, validate_default=False)
    raman_files: RamanFileInfoSet | None = Field(None)
    force_reindex: bool = Field(default=False, validate_default=False)
    persist_to_file: bool = Field(default=True, validate_default=False)

    # Add the private attribute
    _dataset: Dataset | None = PrivateAttr(default=None)

    @computed_field
    @cached_property
    def dataset(self) -> Dataset | None:
        if self._dataset is None and (self.raman_files is None or not self.raman_files):
            logger.debug("Can not construct dataset without raman files.")
            return None
        if self._dataset is not None and not self.force_reindex:
            return self._dataset

        if validate_index_file_path(self.index_file, self.force_reindex):
            dataset = load_dataset_from_file(self.index_file)
            self._dataset = dataset
            return dataset
        self._dataset = self.raman_files.cast_to_dataset()
        return self._dataset

    def __len__(self) -> int:
        if self.raman_files is None:
            return 0
        return len(self.raman_files)

    def __repr__(self):
        return f"{self.__class__.__name__}({len(self.dataset)})"

    def persist_dataset_to_file(self) -> None:
        if (
            self.persist_to_file
            and self.index_file is not None
            and self.dataset is not None
        ):
            if len(self.dataset) == 0:
                logger.warning("Dataset is empty, not writing to file.")
                return
            write_dataset_to_file(self.index_file, self.dataset)

    def read_or_load_data(self) -> None:
        can_reload_from_file = validate_index_file_path(
            self.index_file, self.force_reindex
        )
        if can_reload_from_file:
            self._dataset = load_dataset_from_file(self.index_file)

        validate_and_set_dataset(self.dataset, self.raman_files)

        if self.dataset is not None:
            self.raman_files = RamanFileInfoSet.from_dataset(self.dataset)

        if not self.raman_files and self.dataset is None:
            raise ValueError(
                "Index error, both raman_files and dataset are not provided."
            )
        elif len(self.dataset) == 0:
            raise ValueError("Index error, dataset is empty.")

        self.persist_dataset_to_file()
