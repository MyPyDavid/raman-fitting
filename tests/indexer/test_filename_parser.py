import unittest
import pytest

from pathlib import Path
# from raman_fitting.deconvolution_models import first_order_peaks
import raman_fitting
from raman_fitting.indexer.filename_parser import PathParser



class TestBasePeak(unittest.TestCase):

    sIDs_expected = ['errEMP2_1', 'errTS2_pos1',
                     'testDW38C_pos1', 'testDW38C_pos2',
                     'testDW38C_pos3', 'testDW38C_pos4']

    def test_PathParser(self):
        _dfpath = Path(__file__).parent.parent.parent / 'src' / 'raman_fitting' / 'datafiles'

        _fls = list(_dfpath.rglob('*.txt'))
        _res = []
        for fn in _fls:
            _res.append(PathParser(fn))
        sIDs = [i.parse_result['SampleID'] for i in _res]
        self.assertEqual(sIDs, self.sIDs_expected)

    def test_empty(self):
        PathParser('')

def _test():

    _res = []
    for fn in _fls:
        _res.append(PathParser(fn))
    return _res



if __name__ == '__main__':
    unittest.main()
