import pytest

import numpy as np
from raman_fitting.processing.despike import SpectrumDespiker


int_arrays = (
    np.array([1, 2, 3, 4, 5]),
    np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
    np.array([2, 2, 2, 2, 2, 2, 30, 20, 2, 2, 2, 2, 2, 2])
)

@pytest.mark.parametrize('array', int_arrays)
def test_despiker(array):
    despiker = SpectrumDespiker.model_construct()

    desp_int = despiker.process_intensity(array)
    assert len(desp_int) == len(array)
