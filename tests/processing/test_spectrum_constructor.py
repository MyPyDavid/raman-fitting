from raman_fitting.imports.spectrum.spectrum_constructor import (
    SpectrumDataLoader,
)


def test_spectrum_data_loader_empty():
    spd = SpectrumDataLoader("empty.txt")
    assert spd.file == "empty.txt"
    assert spd.clean_spectrum is None


def test_spectrum_data_loader_file(example_files):
    for file in example_files:
        spd = SpectrumDataLoader(
            file, run_kwargs=dict(sample_id=file.stem, sample_pos=1)
        )
        assert len(spd.clean_spectrum.spectrum) == 1600
        assert len(spd.clean_spectrum.spec_regions) >= 5
