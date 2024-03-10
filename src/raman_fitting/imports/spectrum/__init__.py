from .datafile_parsers import read_file_with_tablib

SPECTRUM_FILETYPE_PARSERS = {
    ".txt": {
        "method": read_file_with_tablib,  # load_spectrum_from_txt,
    },
    ".xlsx": {
        "method": read_file_with_tablib,  # pd.read_excel,
    },
    ".csv": {
        "method": read_file_with_tablib,  # pd.read_csv,
        "kwargs": {},
    },
    ".json": {
        "method": read_file_with_tablib,
    },
}
