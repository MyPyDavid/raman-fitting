import pytest

from raman_fitting.config.path_settings import (
    get_run_mode_paths,
    RunModes,
)
from raman_fitting.imports.files.file_indexer import (
    RamanFileIndex,
    initialize_index_from_source_files,
)
from raman_fitting.imports.models import RamanFileInfo

run_mode = RunModes.PYTEST
run_paths = get_run_mode_paths(run_mode)


@pytest.fixture
def index(example_files, internal_paths, tmp_raman_dir):
    pytest_fixtures_files = list(internal_paths.pytest_fixtures.rglob("*txt"))
    index_file = internal_paths.temp_index_file
    all_test_files = example_files + pytest_fixtures_files
    index = initialize_index_from_source_files(
        index_file=index_file, files=all_test_files, force_reindex=True
    )
    return index


def test_index_make_examples(index, example_files):
    assert isinstance(index, RamanFileIndex)
    assert isinstance(index.raman_files[0], RamanFileInfo)
    assert len(index.dataset) > 1
    assert len(index.dataset) == len(example_files)


# @unittest.skip("export_index not yet implemented")
def test_load_index(index):
    index.index_file.exists()
    new_index = RamanFileIndex(index_file=index.index_file, force_reindex=False)
    assert isinstance(new_index, RamanFileIndex)
