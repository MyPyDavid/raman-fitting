import pathlib

import raman_fitting

import pandas as pd


pd.options.display.max_rows = 10
pd.options.display.max_columns = 10


PACKAGE_ROOT = pathlib.Path(raman_fitting.__file__).resolve().parent
MODEL_DIR = PACKAGE_ROOT / "deconvolution_models"
DATASET_DIR = PACKAGE_ROOT / "datafiles"
RESULTS_DIR = PACKAGE_ROOT / "results"

# index
INDEX_FILE = RESULTS_DIR / 'index.csv'

# data
TESTING_DATA_FILE = "test.csv"
TRAINING_DATA_FILE = "train.csv"
TARGET = "SalePrice"


# variables
FEATURES = []