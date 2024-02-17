import unittest

from raman_fitting.config.settings import (
    InternalPathSettings,
    get_run_mode_paths,
    RunModes,
)
from raman_fitting.imports.files.file_indexer import (
    RamanFileIndex,
    initialize_index_from_source_files,
)
from raman_fitting.imports.files.index_funcs import load_index
from raman_fitting.imports.models import RamanFileInfo

run_mode = RunModes.PYTEST
internal_paths = InternalPathSettings()
run_paths = get_run_mode_paths(run_mode)

# TEST_FIXTURES_PATH = Path(__file__).parent.parent.joinpath("test_fixtures")


class TestIndexer(unittest.TestCase):
    def setUp(self):
        self.example_files = list(internal_paths.example_fixtures.rglob("*txt"))
        self.pytest_fixtures_files = list(internal_paths.pytest_fixtures.rglob("*txt"))

        self.all_test_files = self.example_files + self.pytest_fixtures_files
        index = initialize_index_from_source_files(
            files=self.all_test_files, force_reload=True
        )
        self.index = index

    def test_RamanFileIndex_make_examples(self):
        self.assertIsInstance(self.index, RamanFileIndex)
        self.assertIsInstance(self.index.raman_files[0], RamanFileInfo)
        self.assertGreater(len(self.index.dataset), 1)

        self.assertEqual(len(self.index.dataset), len(self.example_files))

    @unittest.skip("export_index not yet implemented")
    def test_load_index(self):
        _loaded_index = load_index()
        self.assertTrue(isinstance(_loaded_index, RamanFileIndex))


if __name__ == "__main__":
    unittest.main()
    self = TestIndexer()
