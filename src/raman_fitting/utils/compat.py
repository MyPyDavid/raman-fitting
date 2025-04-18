import sys

if sys.version_info < (3, 11):
    from enum import Enum

    class StrEnum(str, Enum):
        """Custom implementation of StrEnum for Python <3.11."""

        def _generate_next_value_(name, start, count, last_values):
            return name.lower()  # Automatically assign lowercase names as values
else:
    from enum import StrEnum  # noqa: F401
