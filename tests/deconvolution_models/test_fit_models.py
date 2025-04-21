import math

import pytest

from raman_fitting.imports.spectrum.parser import load_and_parse_spectrum_from_file
from raman_fitting.models.fit_models import SpectrumFitModel
from raman_fitting.imports.models import SpectrumReader
from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.processing.post_processing import SpectrumProcessor


@pytest.fixture
def clean_spec(example_files, default_regions) -> SpectrumData:
    file = [i for i in example_files if "_pos4" in i.stem][0]

    parsed_spectrum_or_error = load_and_parse_spectrum_from_file(
        file=file,
    )
    spectrum_processor = SpectrumProcessor(
        spectrum=SpectrumReader(
            filepath=file,
            spectrum=parsed_spectrum_or_error).spectrum,
        region_limits=default_regions
        )
    return spectrum_processor.processed_spectra.get_spec_for_region("first_order")


def test_fit_first_order(clean_spec, default_models):
    spectrum = clean_spec
    test_component = "center"
    for model_name, test_model in default_models["first_order"].items():
        # with subTest(model_name=model_name, test_model=test_model):
        spec_fit = SpectrumFitModel(
            **{"spectrum": spectrum, "model": test_model, "region": "first_order"}
        )
        spec_fit.run()
        for component in test_model.lmfit_model.components:
            # with subTest(component=component):
            peak_component = f"{component.prefix}{test_component}"
            fit_value = spec_fit.fit_result.best_values[peak_component]
            init_value = spec_fit.fit_result.init_values[peak_component]
            assert math.isclose(fit_value, init_value, rel_tol=0.05)
            assert spec_fit.fit_result.success
