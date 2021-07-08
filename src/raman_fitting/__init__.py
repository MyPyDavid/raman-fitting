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
    from ._version import version

    __version__ = version
except:
    __version__ = "__version__ = '0.6.11'"


from raman_fitting.config import config

# VERSION_PATH = config.PACKAGE_ROOT / 'VERSION.txt'
# with open(VERSION_PATH, 'r') as version_file:
# TODO change version definitino
# __version__ = version_file.read().strip()


import logging
import sys
import warnings

# Configure logger for use in package
logger = logging.getLogger(__package_name__)
logger.setLevel(logging.DEBUG)
# from raman_fitting.config import logging_config
# logger.addHandler(logging_config.get_console_handler())
# logger.propagate = False

# create console handler
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.DEBUG)

# add the handlers to the logger
logger.addHandler(ch)

# This code is written for Python 3.
if sys.version_info[0] != 3:
    logger.error("raman_fitting requires Python 3.")
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

# from raman_fitting import main_run_fit, indexer

# Other user-facing functions
from .api import *

# TODO list:
# added setup.cfg
# added unittests
# added README.md
# add project.toml only for
# improved logger, each module needs a getlogger(package_name)
# TODO future daemonize the fitting process for using the package and dropping files in the datafiles folder
# TODO add docs with Sphinx, readthedocs
# TODO improve AsyncIO into main delegator processes
# TODO fix plotting because of DeprecationWarning in savefig
# TODO add database for spectrum data storage
# TODO future GUI webinterface
