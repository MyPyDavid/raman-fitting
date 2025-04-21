from pathlib import Path

from attrs import define, field
import logging

from raman_fitting.imports.files.models import RamanFileInfo
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames
from raman_fitting.models.splitter import SpectrumFileRegionSelection
from raman_fitting.utils.compat import StrEnum

logger = logging.getLogger(__name__)


class ErrorType(StrEnum):
    READ_ERROR = "Read Error"
    PROCESSING_ERROR = "Processing Error"
    REGION_ERROR = "Region Error"
    NO_VALID_DATA = "No Valid Data"
    FILE_NOT_FOUND = "File Not Found"
    CASTING_ERROR = "Casting Error"
    NOT_IMPLEMENTED = "Not Implemented"


@define
class FileProcessingError(Exception):
    filepath: str
    error_type: ErrorType
    message: str
    region_name: RegionNames | None = None

    def __str__(self):
        return (
            f"Error processing file {self.filepath} ({self.error_type}): {self.message}"
        )

    def __eq__(self, other):
        if self.region_name is None and other.region is None:
            return self.filepath == other.filepath
        elif self.region_name is None and other.region is not None:
            return False
        elif self.region_name is not None and other.region is None:
            return False
        else:
            return (self.filepath == other.filepath) and (
                self.region_name == other.region
            )


@define
class ErrorHandler:
    errors: list[FileProcessingError] = field(factory=list)

    def add_error(self, error: FileProcessingError):
        self.errors.append(error)
        # logger.error(error)

    def has_errors(self) -> bool:
        return bool(self.errors)

    def get_errors(self) -> list[FileProcessingError]:
        return self.errors

    def get_errors_for_files(
        self, files: list[RamanFileInfo]
    ) -> list[FileProcessingError]:
        _files = set(i.filepath for i in files)
        return [i for i in self.errors if i.filepath in _files]

    def __contains__(
        self, item: Path | FileProcessingError | SpectrumFileRegionSelection
    ):
        region = None
        if isinstance(item, SpectrumFileRegionSelection):
            region = item.region
            item = item.file

        if isinstance(item, RamanFileInfo):
            item = item.filepath

        if isinstance(item, Path):
            return (item, region) in [(i.filepath, i.region_name) for i in self.errors]
        elif isinstance(item, FileProcessingError):
            return item in self.errors

        raise TypeError("Need Path or FileProcessingError")
