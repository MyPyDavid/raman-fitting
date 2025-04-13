"""
Configuration file for pytest and commonly used fixtures
"""

import sys
import pytest
from raman_fitting.config import settings
from raman_fitting.config.path_settings import InternalPathSettings

# Global fixtures
from loguru import logger

logger.enable("raman_fitting")
logger.remove()  # Remove any existing handlers
logger.add(sys.stderr, level="DEBUG", format="{time} - {name} - {message}")


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


@pytest.fixture(autouse=True)
def default_definitions():
    return settings.default_definitions


@pytest.fixture(autouse=True)
def default_regions():
    return settings.default_regions


@pytest.fixture(autouse=True)
def default_models():
    return settings.default_models


@pytest.fixture(autouse=True)
def default_models_first_order(default_models):
    return default_models.get("first_order")


@pytest.fixture(autouse=True)
def default_models_second_order(default_models):
    return default_models.get("second_order")


@pytest.fixture(autouse=True)
def test_sample_id() -> str:
    return "testDW38C"
