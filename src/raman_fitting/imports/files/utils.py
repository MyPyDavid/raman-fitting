from pathlib import Path

from tablib import Dataset

from loguru import logger


def write_dataset_to_file(file: Path, dataset: Dataset) -> None:
    if file.suffix == ".csv":
        with open(file, "w", newline="") as f:
            f.write(dataset.export("csv"))
    else:
        with open(file, "wb", encoding="utf-8") as f:
            f.write(dataset.export(file.suffix))
    logger.debug(f"Wrote dataset {len(dataset)} to {file}")


def load_dataset_from_file(file) -> Dataset:
    with open(file, "r", encoding="utf-8") as fh:
        imported_data = Dataset().load(fh)
    logger.debug(f"Read dataset {len(imported_data)} from {file}")
    return imported_data
