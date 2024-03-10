import pytest

from raman_fitting.imports.spectrumdata_parser import SpectrumReader
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames


def test_spectrum_data_loader_empty():
    with pytest.raises(ValueError):
        SpectrumReader("empty.txt")


def test_spectrum_data_loader_file(example_files):
    for file in example_files:
        sprdr = SpectrumReader(file)
        assert len(sprdr.spectrum.intensity) == 1600
        assert len(sprdr.spectrum.ramanshift) == 1600
        assert sprdr.spectrum.source == file
        assert sprdr.spectrum.region_name == RegionNames.full
