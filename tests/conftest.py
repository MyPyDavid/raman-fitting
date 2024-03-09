"""
Configuration file for pytest and commonly used fixtures
"""
import pytest
from raman_fitting.config.path_settings import InternalPathSettings

# Global fixtures

@pytest.fixture(autouse=True)
def tmp_raman_dir(tmp_path):
    d = tmp_path / "raman-fitting"
    d.mkdir()
    yield d
    d.rmdir()

@pytest.fixture(autouse=True)
def internal_paths():
    return InternalPathSettings()

@pytest.fixture(autouse=True)
def example_files(internal_paths):
    example_files = list(internal_paths.example_fixtures.rglob("*txt"))
    return example_files
