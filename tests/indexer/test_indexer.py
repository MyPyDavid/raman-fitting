import unittest
import pytest

# from raman_fitting.deconvolution_models import first_order_peaks
import raman_fitting
from raman_fitting.indexer.indexer import MakeRamanFilesIndex



class TestBasePeak(unittest.TestCase):


    def test_MakeRamanFilesIndex_make_examples(self):
        RamanIndex = MakeRamanFilesIndex(run_mode ='make_examples')
        self.assertEqual(len(RamanIndex), 6)




if __name__ == '__main__':
    unittest.main()
