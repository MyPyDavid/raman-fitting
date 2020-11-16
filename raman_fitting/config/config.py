import pathlib

#import ..raman_fitting

import pandas as pd


pd.options.display.max_rows = 10
pd.options.display.max_columns = 10


PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL_DIR = PACKAGE_ROOT / "deconvolution_models"
DATASET_DIR = PACKAGE_ROOT / "datafiles"
RESULTS_DIR = PACKAGE_ROOT / "results"

# index
INDEX_FILE = RESULTS_DIR / 'index.csv'
