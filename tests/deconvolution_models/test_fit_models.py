import unittest
import math


from raman_fitting.config.settings import InternalPathSettings
from raman_fitting.models.fit_models import SpectrumFitModel
from raman_fitting.models.deconvolution.base_model import (
    get_models_and_peaks_from_definitions,
)

internal_paths = InternalPathSettings()


class TestFitSpectrum(unittest.TestCase):
    def setUp(self) -> None:
        self.example_files = list(internal_paths.example_fixtures.rglob("*txt"))
        file = [i for i in self.example_files if "_pos4" in i.stem][0]
        self.file = file
        from raman_fitting.imports.spectrumdata_parser import SpectrumReader

        specread = SpectrumReader(file)
        self.specread = specread

        from raman_fitting.processing.post_processing import SpectrumProcessor

        spectrum_processor = SpectrumProcessor(specread.spectrum)
        clean_spec_1st_order = spectrum_processor.clean_spectrum.spec_windows[
            "savgol_filter_raw_window_first_order"
        ]
        clean_spec_1st_order.window_name = "first_order"
        self.clean_spec = clean_spec_1st_order

    def test_fit_first_order(self):
        models = get_models_and_peaks_from_definitions()
        spectrum = self.clean_spec
        test_component = "center"

        for model_name, test_model in models["first_order"].items():
            with self.subTest(model_name=model_name, test_model=test_model):
                spec_fit = SpectrumFitModel(
                    **{"spectrum": spectrum, "model": test_model}
                )
                spec_fit.run_fit()
                for component in test_model.lmfit_model.components:
                    with self.subTest(component=component):
                        # breakpoint()
                        peak_component = f"{component.prefix}{test_component}"
                        fit_value = spec_fit.fit_result.best_values[peak_component]
                        init_value = spec_fit.fit_result.init_values[peak_component]
                        self.assertTrue(
                            math.isclose(fit_value, init_value, rel_tol=0.05)
                        )
                        self.assertTrue(spec_fit.fit_result.success)
                        # print(model_name, peak_component, init_value, fit_value)
