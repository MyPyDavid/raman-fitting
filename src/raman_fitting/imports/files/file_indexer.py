""" Indexer for raman data files """
from itertools import filterfalse, groupby
from pathlib import Path
from typing import List, Sequence, TypeAlias

from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    FilePath,
    NewPath,
    model_validator,
)
from raman_fitting.config import settings
from raman_fitting.imports.collector import collect_raman_file_infos
from raman_fitting.imports.files.utils import (
    load_dataset_from_file,
    write_dataset_to_file,
)
from raman_fitting.imports.models import RamanFileInfo
from tablib import Dataset

RamanFileInfoSet: TypeAlias = List[RamanFileInfo]


class RamanFileIndex(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    index_file: NewPath | FilePath = Field(None, validate_default=False)
    raman_files: RamanFileInfoSet | None = Field(None)
    dataset: Dataset | None = Field(None)
    force_reindex: bool = Field(False, validate_default=False)
    persist_to_file: bool = Field(True, validate_default=False)

    @model_validator(mode="after")
    def read_or_load_data(self) -> "RamanFileIndex":
        if not any([self.index_file, self.raman_files, self.dataset]):
            raise ValueError("Not all fields should be empty.")

        reload_from_file = validate_reload_from_index_file(
            self.index_file, self.force_reindex
        )
        if reload_from_file:
            self.dataset = load_dataset_from_file(self.index_file)
            self.raman_files = parse_dataset_to_index(self.dataset)
            return self

        if self.raman_files is not None:
            dataset_rf = cast_raman_files_to_dataset(self.raman_files)
            if self.dataset is not None:
                assert (
                    dataset_rf == self.dataset
                ), "Both dataset and raman_files provided and they are different."
            self.dataset = dataset_rf

        if self.dataset is not None:
            self.raman_files = parse_dataset_to_index(self.dataset)

        if self.raman_files is None and self.dataset is None:
            raise ValueError(
                "Index error, both raman_files and dataset are not provided."
            )

        if self.persist_to_file and self.index_file is not None:
            write_dataset_to_file(self.index_file, self.dataset)

        return self


def validate_reload_from_index_file(
    index_file: Path | None, force_reindex: bool
) -> bool:
    if index_file is None:
        logger.debug(
            "Index file not provided, index will not be reloaded or persisted."
        )
        return False
    if index_file.exists() and not force_reindex:
        return True
    elif force_reindex:
        logger.warning(
            f"Index index_file file {index_file} exists and will be overwritten."
        )
    else:
        logger.info(
            "Index index_file file does not exists but was asked to reload from it."
        )
    return False


def cast_raman_files_to_dataset(raman_files: List[RamanFileInfo]) -> Dataset:
    headers = list(RamanFileInfo.model_fields.keys())
    data = Dataset(headers=headers)
    for file in raman_files:
        data.append(file.model_dump(mode="json").values())
    return data


def parse_dataset_to_index(dataset: Dataset) -> List[RamanFileInfo]:
    raman_files = []
    for row in dataset:
        row_data = dict(zip(dataset.headers, row))
        raman_files.append(RamanFileInfo(**row_data))
    return raman_files


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
) -> RamanFileInfoSet:
    """loops over the files and scrapes the index data from each file"""
    if not raman_files:
        raman_files = list(settings.internal_paths.example_fixtures.glob("*.txt"))
    index = collect_raman_file_infos(raman_files, **kwargs)
    logger.info(f"successfully made index {len(index)} from {len(raman_files)} files")
    return index


def initialize_index_from_source_files(
    files: Sequence[Path] | None = None, force_reindex: bool = False
) -> RamanFileIndex:
    index_file = settings.destination_dir.joinpath("index.csv")
    raman_files = collect_raman_file_index_info(raman_files=files)
    raman_index = RamanFileIndex(
        index_file=index_file, raman_files=raman_files, force_reindex=force_reindex
    )
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
    main()
