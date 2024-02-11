from pathlib import Path

from tablib import Dataset


def write_dataset_to_file(file: Path, dataset: Dataset) -> None:
    with open(file, "wb", encoding="utf-8") as f:
        f.write(dataset.export(file.suffix))


def load_dataset_from_file(file) -> Dataset:
    with open(file, "r", encoding="utf-8") as fh:
        imported_data = Dataset().load(fh)
    return imported_data
