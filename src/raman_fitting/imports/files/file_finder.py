from typing import List
import logging
from pathlib import Path
from pydantic import BaseModel, DirectoryPath, Field, model_validator

logger = logging.getLogger(__name__)


class FileFinder(BaseModel):
    directory: DirectoryPath
    suffixes: List[str] = Field([".txt"])
    files: List[Path] = Field(None, init_var=False)

    @model_validator(mode="after")
    def parse_metadata_from_filepath(self) -> "FileFinder":
        if self.files is None:
            files = find_files(self.directory, self.suffixes)
            self.files = files

        return self


def find_files(directory: Path, suffixes: List[str]) -> List[Path]:
    """
    Creates a list of all raman type files found in the DATASET_DIR which are used in the creation of the index.
    """

    raman_files = []

    for suffix in suffixes:
        files = list(directory.rglob(f"*{suffix}"))
        raman_files += files

    if not raman_files:
        logger.warning(
            f"find_files warning: the chose data file dir was empty.\n{directory}\mPlease choose another directory which contains your data files."
        )
    # TODO filter files somewhere else
    # raman_files_raw = [i for i in raman_files if not any(k in i for k in excluded)
    #                    "fail" not in i.stem and "Labjournal" not in str(i)
    logger.info(
        f"find_files {len(raman_files)} files were found in the chosen data dir:\n\t{directory}"
    )
    return raman_files
