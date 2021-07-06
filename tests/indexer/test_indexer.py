import datetime
import unittest
from importlib import resources
from pathlib import Path

# from raman_fitting.deconvolution_models import first_order_peaks
import pandas as pd
import pytest

import raman_fitting
from raman_fitting.datafiles import example_files
from raman_fitting.indexer.indexer import MakeRamanFilesIndex


class TestIndexer(unittest.TestCase):
    def setUp(self):

        _example_path = Path(example_files.__path__[0])
        _example_files_contents = list(Path(_example_path).rglob("*txt"))

        self._example_files = [i for i in _example_files_contents]

        self.RamanIndex = MakeRamanFilesIndex(run_mode="make_examples")

    def test_MakeRamanFilesIndex_make_examples(self):

        self.assertEqual(len(self.RamanIndex), len(self._example_files))

    def test_load_index(self):
        _loaded_index = self.RamanIndex.load_index()
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
