from dataclasses import dataclass
import re

import pandas as pd
import numpy as np


@dataclass
class ValidateSpectrumValues:
    spectrum_key: str
    min: float
    max: float
    len: int

    def validate_min(self, spectrum_data: pd.DataFrame):
        data_min = spectrum_data[self.spectrum_key].min()
        return np.isclose(data_min, self.min, rtol=0.2)

    def validate_max(self, spectrum_data: pd.DataFrame):
        data_max = spectrum_data[self.spectrum_key].max()
        return data_max <= self.max

    def validate_len(self, spectrum_data: pd.DataFrame):
        data_len = len(spectrum_data)
        return np.isclose(data_len, self.len, rtol=0.1)

    def validate_spectrum(self, spectrum_data: pd.DataFrame):
        ret = []
        for _func in [self.validate_min, self.validate_max, self.validate_len]:
            ret.append(_func(spectrum_data))
        return all(ret)

