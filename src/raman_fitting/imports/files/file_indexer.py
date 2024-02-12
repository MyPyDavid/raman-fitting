""" Indexer for raman data files """
from itertools import groupby, filterfalse
from typing import List, Sequence
from pathlib import Path

from pydantic import (
    BaseModel,
    FilePath,
    NewPath,
    Field,
    model_validator,
    ConfigDict,
)

from raman_fitting.config import settings
from raman_fitting.imports.collector import collect_raman_file_infos
from raman_fitting.imports.models import RamanFileInfo

from .utils import load_dataset_from_file


from loguru import logger
from tablib import Dataset


class RamanFileIndex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    source: NewPath | FilePath = Field(None, validate_default=False)
    raman_files: Sequence[RamanFileInfo] = Field(None)
    dataset: Dataset = Field(None)
    force_reload: bool = Field(True, validate_default=False)

    @model_validator(mode="after")
    def read_or_load_data(self) -> "RamanFileIndex":
        if not any([self.source, self.raman_files, self.dataset]):
            raise ValueError("Not all fields should be empty.")

        if self.source is not None:
            if self.source.exists() and not self.force_reload:
                self.dataset = load_dataset_from_file(self.source)
                self.raman_files = parse_dataset_to_index(self.dataset)
                return self
            elif self.source.exists() and self.force_reload:
                logger.info(
                    f"Index source file {self.source} exists and will be overwritten."
                )
            elif not self.source.exists() and self.force_reload:
                logger.info(
                    "Index source file does not exists but was asked to reload from it."
                )
            elif not self.source.exists() and not self.force_reload:
                pass
        else:
            logger.debug("Index source file not provided.")

        if self.raman_files is not None:
            if self.dataset is None:
                self.dataset = cast_raman_files_to_dataset(self.raman_files)
            else:
                dataset_rf = cast_raman_files_to_dataset(self.raman_files)
                assert (
                    dataset_rf == self.dataset
                ), "Both dataset and raman_files provider but are different."
        if self.dataset is not None:
            self.raman_files = parse_dataset_to_index(self.dataset)
        elif self.dataset is None and self.raman_files is None:
            raise ValueError(
                "Index error, both raman_files and dataset are not provided."
            )


def cast_raman_files_to_dataset(raman_files: List[RamanFileInfo]) -> Dataset:
    headers = list(RamanFileInfo.model_fields.keys())
    data = Dataset(headers=headers)
    for file in raman_files:
        data.append(file.model_dump(mode="json").values())
    return data


def parse_dataset_to_index(dataset: Dataset) -> List[RamanFileInfo]:
    raman_file = []
    for row in dataset:
        row_data = dict(zip(dataset.headers, row))
        raman_file.append(RamanFileInfo(**row_data))
    return raman_file


class IndexSelector(BaseModel):
    raman_files: Sequence[RamanFileInfo]
    sample_IDs: List[str] = Field(default_factory=list)
    sample_groups: List[str] = Field(default_factory=list)
    selection: Sequence[RamanFileInfo] = Field(default_factory=list)

    @model_validator(mode="after")
    def make_and_set_selection(self) -> "IndexSelector":
        rf_index = self.raman_files
        if not any([self.sample_groups, self.sample_IDs]):
            self.selection = rf_index
            logger.debug(
                f"{self.__class__.__qualname__} selected {len(self.selection)} of {len(rf_index)}. "
            )
            return self
        else:
            rf_index_groups = list(
                filter(lambda x: x.sample.group in self.sample_groups, rf_index)
            )
            _pre_selected_samples = {i.sample.id for i in rf_index_groups}
            selected_sampleIDs = filterfalse(
                lambda x: x in _pre_selected_samples, self.sample_IDs
            )
            rf_index_samples = list(
                filter(lambda x: x.sample.id in selected_sampleIDs, rf_index)
            )
            rf_selection_index = rf_index_groups + rf_index_samples
            self.selection = rf_selection_index
            logger.debug(
                f"{self.__class__.__qualname__} selected {len(self.selection)} of {rf_index}. "
            )
            return self


def groupby_sample_group(index: List[RamanFileInfo]):
    """Generator for Sample Groups, yields the name of group and group of the index SampleGroup"""
    grouper = groupby(index, key=lambda x: x.sample.group)
    return grouper


def groupby_sample_id(index: List[RamanFileInfo]):
    """Generator for SampleIDs, yields the name of group, name of SampleID and group of the index of the SampleID"""
    grouper = groupby(index, key=lambda x: x.sample.id)
    return grouper


def iterate_over_groups_and_sample_id(index: List[RamanFileInfo]):
    for grp_name, grp in groupby_sample_group(index):
        for sample_id, sgrp in groupby_sample_group(grp):
            yield grp_name, grp, sample_id, sgrp


def select_index_by_sample_groups(index: List[RamanFileInfo], sample_groups: List[str]):
    return filter(lambda x: x.sample.group in sample_groups, index)


def select_index_by_sample_ids(index: List[RamanFileInfo], sample_ids: List[str]):
    return filter(lambda x: x.sample.id in sample_ids, index)


def select_index(
    index: List[RamanFileInfo], sample_groups: List[str], sample_ids: List[str]
):
    group_selection = list(select_index_by_sample_groups(index, sample_groups))
    sample_selection = list(select_index_by_sample_ids(index, sample_ids))
    selection = group_selection + sample_selection
    return selection


def collect_raman_file_index_info(
    raman_files: Sequence[Path] | None = None, **kwargs
) -> List[RamanFileInfo]:
    """loops over the files and scrapes the index data from each file"""
    if not raman_files:
        raman_files = list(settings.internal_paths.example_fixtures.glob("*.txt"))
    index = collect_raman_file_infos(raman_files, **kwargs)
    logger.info(f"successfully made index {len(index)} from {len(raman_files)} files")
    return index


def initialize_index(files: Sequence[Path] | None = None, force_reload: bool = False):
    index_file = settings.destination_dir.joinpath("index.csv")
    raman_files = collect_raman_file_index_info(raman_files=files)
    index_data = {
        "file": index_file,
        "raman_files": raman_files,
        "force_reload": force_reload,
    }
    raman_index = RamanFileIndex(**index_data)
    logger.info(
        f"index_delegator index prepared with len {len(raman_index.raman_files)}"
    )
    return raman_index


def main():
    """test run for indexer"""
    index_file = settings.destination_dir.joinpath("index.csv")
    raman_files = collect_raman_file_index_info()
    try:
        index_data = {"file": index_file, "raman_files": raman_files}
        raman_index = RamanFileIndex(**index_data)
        logger.debug(f"Raman Index len: {len(raman_index.dataset)}")
    except Exception as e:
        logger.error(f"Raman Index error: {e}")
    # breakpoint()
    select_index(raman_index.raman_files, sample_groups=["DW"], sample_ids=["DW38"])
    # ds = cast_raman_files_to_dataset(raman_index.raman_files)

    return raman_index


if __name__ == "__main__":
    RamanIndex = main()
