# pylint: disable=W0614,W0611,W0622
# flake8: noqa
# isort:skip_file

__author__ = "David Wallace"
__docformat__ = "restructuredtext"
__status__ = "Development"
__future_package_name__ = "pyramdeconv"
__current_package_name__ = "raman_fitting"
__package_name__ = __current_package_name__


try:
    from ._version import __version__
except ImportError:
    # -- Source mode --
    try:
        # use setuptools_scm to get the current version from src using git
        from setuptools_scm import get_version as _gv
        from os import path as _path

        __version__ = _gv(_path.join(_path.dirname(__file__), _path.pardir))
    except ModuleNotFoundError:
        __version__ = "importerr_modulenotfound_version"
    except Exception as e:
        __version__ = "importerr_exception_version"
except Exception as e:
    __version__ = "catch_exception_version"


import logging
import sys
import warnings

# Configure logger for use in package
logger = logging.getLogger(__package_name__)

log_format = (
    "[%(asctime)s] — %(name)s — %(levelname)s —"
    "%(funcName)s:%(lineno)d—12s %(message)s"
)
# '[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s')

# Define basic configuration
logging.basicConfig(
    # Define logging level
    level=logging.DEBUG,
    # Define the format of log messages
    format=log_format,
    # Provide the filename to store the log messages
    filename=("debug.log"),
)

formatter = logging.Formatter(log_format)
from raman_fitting.config import logging_config

logger.addHandler(logging_config.get_console_handler())

# create console handler
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(ch)

# This code is written for Python 3.
if sys.version_info.major < 3 and sys.version_info.minor < 7:
    logger.error(f"{__package_name__} requires Python 3.7 or higher.")
    sys.exit(1)

# Let users know if they're missing any hard dependencies
hard_dependencies = ("numpy", "pandas", "scipy", "matplotlib", "lmfit")
soft_dependencies = {}
missing_dependencies = []

import importlib

for dependency in hard_dependencies:
    if not importlib.util.find_spec(dependency):
        missing_dependencies.append(dependency)

if missing_dependencies:
    raise ImportError(f"Missing required dependencies {missing_dependencies}")

for dependency in soft_dependencies:
    if not importlib.util.find_spec(dependency):
        warnings.warn(
            f"Missing important package {dependency}. {soft_dependencies[dependency]}"
        )

del hard_dependencies, soft_dependencies, dependency, missing_dependencies

# Main Loop Delegator
from raman_fitting.delegating.main_delegator import MainDelegator, make_examples

# Indexer
from raman_fitting.indexing.indexer import MakeRamanFilesIndex as make_index

# Processing
from raman_fitting.processing.spectrum_template import SpectrumTemplate
from raman_fitting.processing.spectrum_constructor import (
    SpectrumDataLoader,
    SpectrumDataCollection,
)

# Modelling / fitting
from raman_fitting.deconvolution_models.fit_models import InitializeModels, Fitter

# Exporting / Plotting
from raman_fitting.exporting.exporter import Exporter
from raman_fitting.config import filepath_settings
