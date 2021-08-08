import unittest

# import importlib
from importlib import resources
from pathlib import Path

# from raman_fitting.deconvolution_models import first_order_peaks
import raman_fitting
from raman_fitting.datafiles import example_files
from raman_fitting.indexing.filename_parser import PathParser
from raman_fitting.indexing.filename_parser import (
    _extra_sID_name_mapper,
    _extra_overwrite_sID_from_mapper,
)
from raman_fitting.indexing.filename_parser import (
    _extra_sgrpID_name_mapper,
    _extra_overwrite_sgrpID_from_parts,
)

from raman_fitting.indexing.filename_parser_helpers import filestem_to_sid_and_pos

# import pytest


class TestFilenameParser(unittest.TestCase):

    example_parse_expected = {
        "errEMP2_1.txt": ("errEMP2", 1),
        "errTS2_pos1.txt": ("errTS2", 1),
        "Si_spectrum01.txt": ("Si", 1),
        "testDW38C_pos1.txt": ("testDW38C", 1),
        "testDW38C_pos2.txt": ("testDW38C", 2),
        "testDW38C_pos3.txt": ("testDW38C", 3),
        "testDW38C_pos4.txt": ("testDW38C", 4),
        "DW_AB_CD-EF_GE_pos3": ("DW_AB_CD-EF_GE", 3),
        "DW99-pos3": ("DW99", 3),
        "Si": ("Si", 0),
    }

    result_attr = "parse_result"

    def setUp(self):
        _example_path = Path(example_files.__path__[0])
        _example_files_contents = list(Path(_example_path).rglob("*txt"))

        self.datafiles = _example_files_contents
        # list(filter(lambda x: x.endswith('.txt'), _example_files_contents))
        _pathparsers = []
        for fn in self.datafiles:
            _pathparsers.append(PathParser(_example_path.joinpath(fn)))
        self.data_PPs = _pathparsers
        self.empty_PP = PathParser()

        # Make expected results
        # {i.name: (i.parse_result['SampleID'], i.parse_result['SamplePos']) for i in  self.data_PPs}

    def test_PathParser(self):
        self.assertTrue(all(isinstance(i, PathParser) for i in self.data_PPs))
        # Check if instance has results attribute
        self.assertTrue(all(hasattr(i, self.result_attr) for i in self.data_PPs))

    def test_PathParser_empty(self):
        self.assertTrue(hasattr(self.empty_PP, "_flavour"))
        self.assertTrue(hasattr(self.empty_PP, self.result_attr))

    def test_PP_extra_from_map(self):

        for k, val in _extra_sID_name_mapper.items():
            _mapval = _extra_overwrite_sID_from_mapper(k)

            self.assertEqual(_mapval, val)

    def test_PP_extra_from_parts(self):
        self.assertEqual("TEST", _extra_overwrite_sgrpID_from_parts([], "TEST"))

        for k, val in _extra_sgrpID_name_mapper.items():
            emptymap_PP = PathParser(f"{k}/TEST.txt")
            self.assertEqual(
                val,
                _extra_overwrite_sgrpID_from_parts(emptymap_PP.parts, "TEST"),
            )

    def test_PP_parse_filepath_to_sid_and_pos(self):

        for file, _expected in self.example_parse_expected.items():
            self.assertEqual(filestem_to_sid_and_pos(file), _expected)

    # def test_PathParser(self):
    #     _dfpath = Path(__file__).parent.parent.parent / 'src' / 'raman_fitting' / 'datafiles'
    #     _fls = list(_dfpath.rglob('*.txt'))
    #     _res = []
    #     for fn in _fls:
    #         _res.append(PathParser(fn))
    #     sIDs = [i.parse_result['SampleID'] for i in _res]
    #     self.assertEqual(sIDs, self.sIDs_expected)

    # def test_empty(self):
    #     PathParser('')


if __name__ == "__main__":
    unittest.main()
    self = TestFilenameParser()
    self.setUp()
