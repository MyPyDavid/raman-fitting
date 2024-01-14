import unittest

# import importlib
from pathlib import Path

from raman_fitting.imports.models import RamanFileInfo
from raman_fitting.imports.samples.sample_id_helpers import (
    overwrite_sID_from_mapper,
    overwrite_sgrpID_from_parts,
)


from raman_fitting.imports.samples.sample_id_helpers import (
    parse_string_to_sample_id_and_position,
)

# import pytest
TEST_FIXTURES_PATH = Path(__file__).parent.parent.joinpath("test_fixtures")


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
    sID_name_mapper = {}
    sGrp_name_mapper = {}

    def setUp(self):
        _example_path = TEST_FIXTURES_PATH
        _example_files_contents = list(Path(_example_path).rglob("*txt"))

        self.datafiles = _example_files_contents
        # list(filter(lambda x: x.endswith('.txt'), _example_files_contents))
        _pathparsers = []
        for fn in self.datafiles:
            _pathparsers.append(RamanFileInfo(**{"file": _example_path.joinpath(fn)}))
        self.data_PPs = _pathparsers
        # self.empty_PP = RamanFileInfo()

        # Make expected results
        # {i.name: (i.parse_result['SampleID'], i.parse_result['SamplePos']) for i in  self.data_PPs}

    def test_RamanFileInfo(self):
        self.assertTrue(all(isinstance(i, RamanFileInfo) for i in self.data_PPs))

    def test_PP_extra_from_map(self):
        for k, val in self.sID_name_mapper.items():
            _mapval = overwrite_sID_from_mapper(k, self.sID_name_mapper)

            self.assertEqual(_mapval, val)

    def test_PP_extra_from_parts(self):
        self.assertEqual(
            "TEST", overwrite_sgrpID_from_parts([], "TEST", self.sGrp_name_mapper)
        )
        for k, val in self.sGrp_name_mapper.items():
            emptymap_PP = RamanFileInfo(f"{k}/TEST.txt")
            self.assertEqual(
                val,
                overwrite_sgrpID_from_parts(
                    emptymap_PP.parts, "TEST", self.sGrp_name_mapper
                ),
            )

    def test_PP_parse_filepath_to_sid_and_pos(self):
        for file, _expected in self.example_parse_expected.items():
            self.assertEqual(parse_string_to_sample_id_and_position(file), _expected)


if __name__ == "__main__":
    unittest.main()
    self = TestFilenameParser()
    self.setUp()
