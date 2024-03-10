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

import sys
import warnings

from loguru import logger

# This code is written for Python 3.11 and higher
if sys.version_info.major < 3 and sys.version_info.minor < 11:
    logger.error(f"{__package_name__} requires Python 3.11 or higher.")
    sys.exit(1)

# Let users know if they're missing any hard dependencies
hard_dependencies = ("numpy", "pandas", "scipy", "matplotlib", "lmfit", "pydantic")
soft_dependencies = {}
missing_dependencies = []

import importlib.util

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
from raman_fitting.imports.files.file_indexer import RamanFileIndex

# Processing
from raman_fitting.imports.spectrum.spectrum_constructor import SpectrumDataLoader
# from raman_fitting.imports.spectrum.spectra_collection import SpectrumDataCollection


# Modelling / fitting
from raman_fitting.models.deconvolution.init_models import InitializeModels

# Exporting / Plotting
from raman_fitting.exports.exporter import ExportManager
