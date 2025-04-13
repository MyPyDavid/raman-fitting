from dataclasses import dataclass
import logging

import numpy as np
from tablib import Dataset

from raman_fitting.imports.spectrum.datafile_schema import SpectrumDataKeys

logger = logging.getLogger(__name__)


def validate_min(spectrum_data, min_value: float):
    if not min_value <= min(spectrum_data):
        raise ValueError(f"Minium value {min(spectrum_data)} is lower than {min_value}")


def validate_max(spectrum_data, max_value: float):
    if not max(spectrum_data) <= max_value:
        raise ValueError(
            f"Maximum value {max(spectrum_data)} is greater than {max_value}"
        )


def validate_len(spectrum_data, len_value: int):
    if not np.isclose(len(spectrum_data), len_value, rtol=0.1):
        raise ValueError(
            f"Length {len(spectrum_data)} differs from expected {len_value}"
        )


@dataclass
class ValidateSpectrumValues:
    spectrum_key: str
    min: float
    max: float
    len: int | None = None

    def validate(self, spectrum_data) -> tuple[bool, list]:
        errors = []
        for validator, expected_value in [
            (validate_min, self.min),
            (validate_max, self.max),
            (validate_len, self.len),
        ]:
            if expected_value is None:
                continue

            try:
                validator(spectrum_data, expected_value)
            except ValueError as e:
                errors.append(e)

        return not errors, errors


def validate_spectrum_keys_expected_values(
    spectrum_data: Dataset, expected_values: ValidateSpectrumValues
):
    if expected_values.spectrum_key not in spectrum_data.columns:
        logger.error(
            f"The expected value type {expected_values.spectrum_key} is not in the columns {spectrum_data.columns}"
        )
    if spectrum_data.empty:
        logger.error("Spectrum data is empty")
        return

    validation = expected_values.validate(spectrum_data)

    if not validation:
        logger.warning(
            f"The {expected_values.spectrum_key} of this spectrum does not match the expected values {expected_values}"
        )


SPECTRUM_KEYS_EXPECTED_VALUES = {
    SpectrumDataKeys.RAMANSHIFT: ValidateSpectrumValues(
        spectrum_key=SpectrumDataKeys.RAMANSHIFT, min=-95, max=3750
    ),
    SpectrumDataKeys.INTENSITY: ValidateSpectrumValues(
        spectrum_key=SpectrumDataKeys.INTENSITY, min=0, max=1e5
    ),
}
