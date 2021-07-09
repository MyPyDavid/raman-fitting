import unittest
from pathlib import Path

import numpy as np
import pytest

from raman_fitting.datafiles import example_files
from raman_fitting.processing.cleaner import Despiker


class TestDespiker(unittest.TestCase):
    def test_Despiker(self):

        desp = Despiker(np.array([1, 2, 3, 4, 5]))
        self.assertEqual(len(desp.df), 5)

        desp = Despiker(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        self.assertEqual(len(desp.df), 10)

        desp = Despiker(np.array([2, 2, 2, 2, 2, 2, 30, 20, 2, 2, 2, 2, 2, 2]))


def _debugging():

    self = TestDespiker()
    desp = Despiker(np.array([2, 2, 2, 2, 2, 2, 30, 20, 2, 2, 2, 2, 2, 2]))
    desp.plot_Z()
    intensity = desp.result["input_intensity"]
    Z_t_filtered = desp.result["Z_t_filtered"]
    moving_window_size = desp.moving_window_size
    Z_threshold = desp.Z_threshold


if __name__ == "__main__":
    unittest.main()
