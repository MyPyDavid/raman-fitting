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


def _debugging():

    self = TestDespiker()


if __name__ == "__main__":
    unittest.main()
