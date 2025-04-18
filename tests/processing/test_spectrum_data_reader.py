from pathlib import Path

import pytest

from raman_fitting.imports.spectrumdata_parser import SpectrumReader
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames


def test_spectrum_data_loader_empty():
    with pytest.raises(ValueError):
        SpectrumReader(filepath="empty.txt")


def test_spectrum_data_loader_file(example_files):
    for file in example_files:
        sprdr = SpectrumReader(filepath=file)
        assert len(sprdr.spectrum.intensity) > 1590
        assert len(sprdr.spectrum.ramanshift) > 1590
        assert len(sprdr.spectrum.intensity) == len(sprdr.spectrum.ramanshift)
        assert sprdr.spectrum.source == file
        assert sprdr.spectrum.region_name == RegionNames.FULL


def test_spectrum_hash_consistency(example_files):
    """Test that identical files produce identical hashes."""
    # Same file should produce same hash
    reader1 = SpectrumReader(filepath=example_files[0])
    reader2 = SpectrumReader(filepath=example_files[0])
    assert reader1.spectrum_hash == reader2.spectrum_hash

    # Different files should have different hashes
    if len(example_files) > 1:
        reader3 = SpectrumReader(filepath=example_files[1])
        assert reader1.spectrum_hash != reader3.spectrum_hash


def test_spectrum_length_computation(example_files):
    """Test that spectrum_length is computed correctly."""
    reader = SpectrumReader(filepath=example_files[0])
    assert reader.spectrum_length == len(reader.spectrum)
    assert reader.spectrum_length > 1590


def test_immutability(example_files):
    """Test that the model is truly immutable."""
    reader = SpectrumReader(filepath=example_files[0])

    with pytest.raises(Exception):  # Type of exception depends on Pydantic version
        reader.label = "new_label"

    with pytest.raises(Exception):
        reader.filepath = Path("different.txt")


def test_custom_region(example_files):
    """Test that custom labels and regions are properly set."""
    custom_region = "G_BAND"
    with pytest.raises(ValueError):
        SpectrumReader(
            filepath=example_files[0], region_name=custom_region
        ).model_dump()


@pytest.mark.parametrize(
    "invalid_path",
    [
        "",  # empty string
        "nonexistent/path/file.txt",  # non-existent path
        ".",  # directory instead of file
    ],
)
def test_invalid_filepath(invalid_path):
    """Test that invalid file paths are properly handled."""
    with pytest.raises((FileNotFoundError, ValueError)):
        SpectrumReader(filepath=invalid_path)


def test_cached_property_behavior(example_files):
    """Test that computed fields are properly cached."""
    reader = SpectrumReader(filepath=example_files[0])

    # First access computes the value
    hash1 = reader.spectrum_hash
    length1 = reader.spectrum_length

    # Second access should return cached value
    hash2 = reader.spectrum_hash
    length2 = reader.spectrum_length

    assert hash1 == hash2
    assert length1 == length2

    # Verify they're the same object in memory
    assert id(hash1) == id(hash2)
    assert id(length1) == id(length2)


@pytest.fixture
def sample_readers(example_files):
    """Fixture to create sample readers for testing."""
    return [SpectrumReader(filepath=file) for file in example_files]


def test_model_dump_json(sample_readers):
    """Test that model can be serialized to JSON."""
    reader = sample_readers[0]
    json_data = reader.model_dump_json()
    assert isinstance(json_data, str)
    assert reader.filepath.name in json_data
    assert reader.label in json_data
