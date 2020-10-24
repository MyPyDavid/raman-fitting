#from .indexer import *
#from .main_run_fit import * 
#from .plotting import *
#from .post_process import *
#from .spectrum_analyzer import *

import logging

from raman_fitting.config import config
from raman_fitting.config import logging_config


VERSION_PATH = config.PACKAGE_ROOT / 'VERSION'

# Configure logger for use in package
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging_config.get_console_handler())
logger.propagate = False


with open(VERSION_PATH, 'r') as version_file:
    __version__ = version_file.read().strip()
