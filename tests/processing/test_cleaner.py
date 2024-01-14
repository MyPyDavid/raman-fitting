import unittest

import numpy as np


from raman_fitting.processing.despike import SpectrumDespiker


class TestDespiker(unittest.TestCase):
    def test_Despiker(self):
        despiker = SpectrumDespiker.model_construct()

        _int = np.array([1, 2, 3, 4, 5])
        desp_int = despiker.process_intensity(_int)
        self.assertEqual(len(desp_int), len(_int))

        _int = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        desp_int = despiker.process_intensity(_int)
        self.assertEqual(len(desp_int), len(_int))

        _int = np.array([2, 2, 2, 2, 2, 2, 30, 20, 2, 2, 2, 2, 2, 2])
        desp_int = despiker.process_intensity(_int)
        self.assertEqual(len(desp_int), len(_int))


if __name__ == "__main__":
    unittest.main()
