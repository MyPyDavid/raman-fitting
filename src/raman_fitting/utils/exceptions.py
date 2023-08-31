class prdError(Exception):
    """Base error raised by pyramdeconv."""


class MainDelegatorError(prdError):
    """Raised when a method in the main delegator fails."""
