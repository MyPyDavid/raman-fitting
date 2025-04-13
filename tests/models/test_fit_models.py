from raman_fitting.imports.spectrumdata_parser import SpectrumReader
from raman_fitting.models.deconvolution.spectrum_regions import (
    get_default_regions_from_toml_files,
)
from raman_fitting.models.fit_models import SpectrumFitModel
from raman_fitting.processing.post_processing import SpectrumProcessor


def test_fit_model(example_files, default_models_first_order):
    file = [i for i in example_files if "_pos4" in i.stem][0]

    spectrum_processor = SpectrumProcessor(
        SpectrumReader(file).spectrum,
        region_limits=get_default_regions_from_toml_files(),
    )
    clean_spec_1st_order = spectrum_processor.processed_spectra.get_spec_for_region(
        "first_order"
    )

    spec_fit = SpectrumFitModel(
        spectrum=clean_spec_1st_order,
        model=default_models_first_order["2peaks"],
        region=clean_spec_1st_order.region_name,
    )
    spec_fit.run()
    assert spec_fit.fit_result.success
    assert spec_fit.fit_result.best_values
    assert spec_fit.param_result["ratios"]["center"]["ratio_d_to_g"]["ratio"] < 1
    assert spec_fit.param_result["ratios"]["center"]["ratio_la_d_to_g"]["ratio"] < 10
    d_amp_ = spec_fit.fit_result.best_values["D_amplitude"]
    g_amp_ = spec_fit.fit_result.best_values["G_amplitude"]
    dg_ratio = d_amp_ / g_amp_
    assert (
        spec_fit.param_result["ratios"]["amplitude"]["ratio_d_to_g"]["ratio"]
        == dg_ratio
    )
