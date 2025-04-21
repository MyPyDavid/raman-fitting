"""
Pydantic models for Raman spectroscopy file information.

Contains async-compatible models for processing Raman spectroscopy file metadata
and sample information.

Created: 2025-04-18 12:08:49
Author: MyPyDavid
"""

from typing import Sequence
import asyncio
from functools import cached_property

from pydantic import BaseModel, FilePath, computed_field, Field
from tablib import Dataset
from tablib.exceptions import InvalidDimensions
from loguru import logger

from raman_fitting.imports.samples.sample_id_helpers import (
    extract_sample_metadata_from_filepath,
)
from raman_fitting.imports.files.metadata import FileMetaData, get_file_metadata
from raman_fitting.imports.files.utils import get_filename_id_from_path
from raman_fitting.imports.samples.models import SampleMetaData


class RamanFileInfo(BaseModel):
    """
    Model representing a single Raman spectroscopy file with its metadata.

    Provides both sync and async interfaces for file operations.
    """

    filepath: FilePath

    model_config = {
        "arbitrary_types_allowed": True,
        "frozen": True,  # Make the model immutable
    }

    @computed_field
    @cached_property  # Cache the result since filename won't change
    def filename_id(self) -> str:
        """Get unique identifier from file path."""
        return get_filename_id_from_path(self.filepath)

    @computed_field
    @cached_property
    def sample(self) -> SampleMetaData:
        """Extract sample metadata from file path."""
        return extract_sample_metadata_from_filepath(self.filepath)

    @computed_field
    @cached_property
    def file_metadata(self) -> FileMetaData:
        """Get file metadata."""
        return FileMetaData(**get_file_metadata(self.filepath))

    @classmethod
    async def create_async(cls, file: FilePath) -> "RamanFileInfo":
        """
        Asynchronously create a RamanFileInfo instance.

        Args:
            file: Path to the Raman spectroscopy file

        Returns:
            RamanFileInfo instance
        """
        loop = asyncio.get_running_loop()
        # Run synchronous file operations in thread pool
        _metadata = await loop.run_in_executor(None, get_file_metadata, file)
        return cls(
            filepath=file,
        )

    def __hash__(self):
        return hash(self.filepath)

    def __eq__(self, other):
        if isinstance(other, RamanFileInfo):
            return self.filepath == other.filepath
        return False

    def __str__(self):
        return f"{self.sample} in {self.filepath.name}"


class RamanFileInfoSet(BaseModel):
    """
    Collection of RamanFileInfo objects with dataset conversion capabilities.

    Supports both sync and async operations for bulk processing.
    """

    raman_files: Sequence[RamanFileInfo] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
        "frozen": True,  # Make the model immutable
    }

    @classmethod
    def from_dataset(cls, dataset: Dataset) -> "RamanFileInfoSet":
        """Create RamanFileInfoSet from a tablib Dataset."""
        raman_files = [
            RamanFileInfo(**dict(zip(dataset.headers, row))) for row in dataset
        ]
        return cls(raman_files=raman_files)

    @classmethod
    async def create_async(cls, files: Sequence[FilePath]) -> "RamanFileInfoSet":
        """
        Asynchronously create RamanFileInfoSet from a sequence of files.

        Args:
            files: Sequence of file paths to process

        Returns:
            RamanFileInfoSet instance
        """
        tasks = [RamanFileInfo.create_async(file) for file in files]
        raman_files = await asyncio.gather(*tasks)
        return cls(raman_files=raman_files)

    def __len__(self) -> int:
        return len(self.raman_files)

    def __getitem__(self, index: int) -> RamanFileInfo:
        return self.raman_files[index]

    def __iter__(self):
        return iter(self.raman_files)

    def cast_to_dataset(self) -> Dataset | None:
        """Convert the RamanFileInfoSet to a tablib Dataset."""
        headers = list(RamanFileInfo.model_fields.keys()) + list(
            RamanFileInfo.model_computed_fields.keys()
        )
        data = Dataset(headers=headers)

        for file in self.raman_files:
            try:
                data.append(file.model_dump(mode="json").values())
            except InvalidDimensions as exc:
                logger.error(f"Error adding file {file.filename_id} to dataset: {exc}")

        if not data:
            logger.error(
                f"No data was added to the dataset for {len(self.raman_files)} files."
            )
            return None

        return data

    async def cast_to_dataset_async(self) -> Dataset | None:
        """
        Asynchronously convert the RamanFileInfoSet to a tablib Dataset.

        This method processes the model dumps concurrently for better performance
        with large datasets.
        """
        headers = list(RamanFileInfo.model_fields.keys()) + list(
            RamanFileInfo.model_computed_fields.keys()
        )
        data = Dataset(headers=headers)

        loop = asyncio.get_running_loop()

        async def process_file(file: RamanFileInfo):
            try:
                # Run model_dump in thread pool as it might be CPU-intensive
                dump = await loop.run_in_executor(
                    None, lambda: file.model_dump(mode="json")
                )
                return list(dump.values())
            except Exception as exc:
                logger.error(f"Error processing file {file.filename_id}: {exc}")
                return None

        tasks = [process_file(file) for file in self.raman_files]
        results = await asyncio.gather(*tasks)

        # Filter out None results and add to dataset
        valid_results = [r for r in results if r is not None]

        if not valid_results:
            logger.error(
                f"No data was added to the dataset for {len(self.raman_files)} files."
            )
            return None

        for result in valid_results:
            data.append(result)

        return data


# Example usage
async def process_raman_files(files: Sequence[FilePath]) -> Dataset | None:
    """
    Process multiple Raman files asynchronously and convert to dataset.

    Args:
        files: Sequence of file paths to process

    Returns:
        Dataset containing processed file information or None if processing failed
    """
    raman_set = await RamanFileInfoSet.create_async(files)
    return await raman_set.cast_to_dataset_async()
