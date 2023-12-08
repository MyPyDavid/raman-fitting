import unittest

import numpy as np


from raman_fitting.processing.cleaner import Despiker


class TestDespiker(unittest.TestCase):
    def test_Despiker(self):
        desp = Despiker(np.array([1, 2, 3, 4, 5]))
        self.assertEqual(len(desp.df), 5)

        desp = Despiker(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        self.assertEqual(len(desp.df), 10)

        desp = Despiker(np.array([2, 2, 2, 2, 2, 2, 30, 20, 2, 2, 2, 2, 2, 2]))


if __name__ == "__main__":
    unittest.main()
