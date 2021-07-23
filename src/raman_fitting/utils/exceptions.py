class prdError(Exception):
    """Base error raised by pyramdeconv."""


class MainDelegatorError(prdError):
    """Raised when a method in the main delegator fails."""


class DataBaseError(prdError):
    """Raised when interaction with the default database fails"""
