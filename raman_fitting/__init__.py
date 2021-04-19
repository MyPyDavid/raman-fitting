#from .indexer import *
#from .main_run_fit import * 
#from .plotting import *
#from .post_process import *
#from .spectrum_analyzer import *
import logging
import sys

from raman_fitting.config import config


VERSION_PATH = config.PACKAGE_ROOT / 'VERSION'
__author__ = 'David W'
with open(VERSION_PATH, 'r') as version_file:
    __version__ = version_file.read().strip()


# Configure logger for use in package
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# from raman_fitting.config import logging_config
# logger.addHandler(logging_config.get_console_handler())
logger.propagate = False

# create console handler
ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)

# add the handlers to the logger
logger.addHandler(ch)



# This code is written for Python 3.
if sys.version_info[0] != 3:
    logger.error("pyGAPS requires Python 3.")
    sys.exit(1)

# Let users know if they're missing any hard dependencies
hard_dependencies = ("numpy", "pandas", "scipy", "matplotlib")
soft_dependencies = { }
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




from raman_fitting import main_run_fit, indexer



