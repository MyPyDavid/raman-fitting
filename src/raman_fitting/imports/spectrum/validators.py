from dataclasses import dataclass
import logging

import pandas as pd
import numpy as np
from tablib import Dataset

logger = logging.getLogger(__name__)


@dataclass
class ValidateSpectrumValues:
    spectrum_key: str
    min: float
    max: float
    len: int

    def validate_min(self, spectrum_data: pd.DataFrame):
        data_min = min(spectrum_data[self.spectrum_key])
        return np.isclose(data_min, self.min, rtol=0.2)

    def validate_max(self, spectrum_data: pd.DataFrame):
        data_max = max(spectrum_data[self.spectrum_key])
        return data_max <= self.max

    def validate_len(self, spectrum_data: pd.DataFrame):
        data_len = len(spectrum_data)
        return np.isclose(data_len, self.len, rtol=0.1)

    def validate(self, spectrum_data: pd.DataFrame):
        ret = []
        for _func in [self.validate_min, self.validate_max, self.validate_len]:
            ret.append(_func(spectrum_data))
        return all(ret)


def validate_spectrum_keys_expected_values(
    spectrum_data: Dataset, expected_values: ValidateSpectrumValues
):
    if not expected_values.spectrum_key not in spectrum_data.columns:
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
