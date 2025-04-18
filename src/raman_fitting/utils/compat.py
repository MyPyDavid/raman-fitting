import sys
from enum import Enum

if sys.version_info < (3, 11):

    class StrEnum(str, Enum):
        """Custom implementation of StrEnum for Python <3.11."""

        def _generate_next_value_(name, start, count, last_values):
            return name.lower()  # Automatically assign lowercase names as values
else:
    pass
