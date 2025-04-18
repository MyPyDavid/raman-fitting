from enum import auto
from raman_fitting.utils.compat import StrEnum


class SpectrumDataKeys(StrEnum):
    RAMANSHIFT = auto()
    INTENSITY = auto()
    FREQUENCY = auto()
    WAVENUMBER = auto()
    WAVELENGTH = auto()
    COUNTS = auto()
    COUNT = auto()
    COUNT_RATE = auto()
    COUNT_RATE_ERROR = auto()


def get_default_expected_header_keys() -> tuple[SpectrumDataKeys, SpectrumDataKeys]:
    return SpectrumDataKeys.RAMANSHIFT, SpectrumDataKeys.INTENSITY


DEFAULT_SORT_BY_DATA_KEY = SpectrumDataKeys.RAMANSHIFT
