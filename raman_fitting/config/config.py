import pathlib

#import ..raman_fitting

import pandas as pd
from .logging_config import get_console_handler

pd.options.display.max_rows = 10
pd.options.display.max_columns = 10


PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent.parent

MODEL_DIR = PACKAGE_ROOT / "deconvolution_models"
DATASET_DIR = PACKAGE_ROOT / "datafiles"
RESULTS_DIR = PACKAGE_ROOT / "results"

# index
INDEX_FILE = RESULTS_DIR / 'index.csv'
if pathlib.Path(__file__).parent.joinpath('local_config.py').is_file():
    try:
        from .local_config import PACKAGE_ROOT, MODEL_DIR, DATASET_DIR, RESULTS_DIR, INDEX_FILE
        print(f'Importing settings from local config...{RESULTS_DIR}.\n',f'From file: {__name__}')
    except Exception as e:
        print(f'Failed importing settings from local config...{RESULTS_DIR}')