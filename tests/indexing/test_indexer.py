import datetime
import unittest

# from raman_fitting.models.deconvolution import first_order_peaks
import pandas as pd

from raman_fitting.config.settings import (
    InternalPathSettings,
    get_run_mode_paths,
    RunModes,
)
from raman_fitting.imports.files.file_indexer import RamanFileIndex
from raman_fitting.imports.files.index_funcs import load_index
# from raman_fitting.example_fixtures import example_files

run_mode = RunModes.PYTEST
internal_paths = InternalPathSettings()
run_paths = get_run_mode_paths(run_mode)

# TEST_FIXTURES_PATH = Path(__file__).parent.parent.joinpath("test_fixtures")


class TestIndexer(unittest.TestCase):
    def setUp(self):
        self.example_files = list(internal_paths.example_fixtures.rglob("*txt"))
        self.pytest_fixtures_files = list(internal_paths.pytest_fixtures.rglob("*txt"))

        self.all_test_files = self.example_files + self.pytest_fixtures_files

        self.RamanIndex = RamanFileIndex(run_mode=run_mode, source=run_paths.index_file)

    def test_RamanFileIndex_make_examples(self):
        self.assertEqual(len(self.RamanIndex), len(self.example_files))

    @unittest.skip("export_index not yet implemented")
    def test_load_index(self):
        _loaded_index = load_index()
        self.assertTrue(isinstance(_loaded_index, pd.DataFrame))

        for col in _loaded_index.columns:
            _setload = set(_loaded_index[col].values)

            _setindex = set(self.RamanIndex.index[col].values)
            if all(isinstance(i, datetime.date) for i in list(_setindex)):
                # Convert pandas, np.datetime to normal dt
                _setload = set([pd.to_datetime(i).date() for i in list(_setload)])

            self.assertEqual(_setload, _setindex)


if __name__ == "__main__":
    unittest.main()
    self = TestIndexer()
