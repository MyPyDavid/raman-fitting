from tablib import Dataset, detect_format


def load_dataset_from_file(filepath, **kwargs) -> Dataset:
    _format = detect_format(filepath)
    if _format is None:
        _format = "csv"
    with open(filepath, "r") as fh:
        imported_data = Dataset(**kwargs).load(fh, format=_format)
    return imported_data
