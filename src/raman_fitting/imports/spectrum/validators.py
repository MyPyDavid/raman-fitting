from dataclasses import dataclass
import logging

import numpy as np

from raman_fitting.imports.spectrum.datafile_schema import SpectrumDataKeys

logger = logging.getLogger(__name__)


def validate_min(spectrum_data, min_value: float):
    if min(spectrum_data) < min_value:
        raise ValueError(f"Minium value {min(spectrum_data)} is lower than {min_value}")


def validate_max(spectrum_data, max_value: float):
    if max(spectrum_data) > max_value:
        raise ValueError(
            f"Maximum value {max(spectrum_data)} is greater than {max_value}"
        )


def validate_len(spectrum_data, len_value: int):
    if not np.isclose(len(spectrum_data), len_value, rtol=0.1):
        raise ValueError(
            f"Length {len(spectrum_data)} differs from expected {len_value}"
        )


@dataclass(frozen=True)
class ValidateSpectrumValues:
    spectrum_key: str
    min: float
    max: float
    len: int | None = None


def validate_values(
    spectrum_data: list[float | int], expected_values: ValidateSpectrumValues
) -> tuple[bool, list]:
    errors = []
    for validator, expected_value in [
        (validate_min, expected_values.min),
        (validate_max, expected_values.max),
        (validate_len, expected_values.len),
    ]:
        if expected_value is None:
            continue

        try:
            validator(spectrum_data, expected_value)
        except ValueError as e:
            errors.append(e)

    return bool(not errors), errors


SPECTRUM_KEYS_EXPECTED_VALUES = {
    SpectrumDataKeys.RAMANSHIFT: ValidateSpectrumValues(
        spectrum_key=SpectrumDataKeys.RAMANSHIFT, min=-95, max=3750
    ),
    SpectrumDataKeys.INTENSITY: ValidateSpectrumValues(
        spectrum_key=SpectrumDataKeys.INTENSITY, min=0, max=1e5
    ),
}
