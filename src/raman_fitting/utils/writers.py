from pathlib import Path

from loguru import logger
from tablib import Dataset


def write_dataset_to_file(file: Path, dataset: Dataset) -> None:
    if file.suffix == ".csv":
        with open(file, "w", newline="") as f:
            f.write(dataset.export("csv"))
    else:
        with open(file, "wb", encoding="utf-8") as f:
            f.write(dataset.export(file.suffix))
    logger.debug(f"Wrote dataset of len {len(dataset)} to {file}")
