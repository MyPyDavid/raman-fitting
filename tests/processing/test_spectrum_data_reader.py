from pathlib import Path

import pytest

from raman_fitting.imports.errors import FileProcessingError
from raman_fitting.imports.models import SpectrumReader
from raman_fitting.imports.spectrum.parser import load_and_parse_spectrum_from_file
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames


def test_spectrum_data_loader_empty():

    parsed_spectrum_or_error = load_and_parse_spectrum_from_file(
        'empty.txt',
    )
    assert isinstance(parsed_spectrum_or_error, FileProcessingError)


def test_spectrum_data_loader_file(example_files):
    for file in example_files:
        spectrum = load_and_parse_spectrum_from_file(
            file
        )

        assert len(spectrum.intensity) > 1590
        assert len(spectrum.ramanshift) > 1590
        assert len(spectrum.intensity) == len(spectrum.ramanshift)
        assert spectrum.source == file
        assert spectrum.region == RegionNames.FULL


def test_spectrum_hash_consistency(example_files):
    """Test that identical files produce identical hashes."""
    # Same file should produce same hash

    reader1 = load_and_parse_spectrum_from_file(example_files[0])
    reader2 = load_and_parse_spectrum_from_file(example_files[0])
    assert reader1.spectrum_hash == reader2.spectrum_hash

    # Different files should have different hashes
    if len(example_files) > 1:
        reader3 = load_and_parse_spectrum_from_file(example_files[1])
        assert reader1.spectrum_hash != reader3.spectrum_hash


def test_spectrum_length_computation(example_files):
    """Test that spectrum_length is computed correctly."""
    spectrum = load_and_parse_spectrum_from_file(example_files[0])
    assert spectrum.length == len(spectrum)
    assert spectrum.length > 1590


def test_immutability(example_files):
    """Test that the model is truly immutable."""
    spectrum = load_and_parse_spectrum_from_file(example_files[0])

    with pytest.raises(Exception):  # Type of exception depends on Pydantic version
        spectrum.label = "new_label"

    with pytest.raises(Exception):
        spectrum.filepath = Path("different.txt")


def test_custom_region(example_files):
    """Test that custom labels and regions are properly set."""
    with pytest.raises(ValueError):
        load_and_parse_spectrum_from_file(
            example_files[0],
            region_name="NO_NAME_BAND"
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
    error = load_and_parse_spectrum_from_file(invalid_path)
    assert isinstance(error, FileProcessingError)


def test_cached_property_behavior(example_files):
    """Test that computed fields are properly cached."""
    spectrum = load_and_parse_spectrum_from_file(example_files[0])

    # First access computes the value
    hash1 = spectrum.spectrum_hash
    length1 = spectrum.length

    # Second access should return cached value
    hash2 = spectrum.spectrum_hash
    length2 = spectrum.length

    assert hash1 == hash2
    assert length1 == length2

    # Verify they're the same object in memory
    assert id(hash1) == id(hash2)
    assert id(length1) == id(length2)


@pytest.fixture
def sample_readers(example_files):
    """Fixture to create sample readers for testing."""
    return [
        SpectrumReader(
            filepath=file,
            spectrum=load_and_parse_spectrum_from_file(file)
        )
        for file in example_files
    ]


def test_model_dump_json(sample_readers):
    """Test that model can be serialized to JSON."""
    reader = sample_readers[0]
    json_data = reader.model_dump_json()
    assert isinstance(json_data, str)
    assert reader.filepath.name in json_data
    assert reader.label in json_data
