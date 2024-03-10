import pytest

from raman_fitting.models.post_deconvolution.calculate_params import ratio_funcs


result_first = {"D_center": 1, "G_center": 2, "D1D1_center": 3}
first_peaks = "G+D+D2+D3+D4+D5"
result_second = (
    {"D4D4 +D1D1+GD1+D2D2"},
    {"D_center": 1, "G_center": 2, "D1D1_center": 3},
)
var_name = "peak"


@pytest.fixture
def list_of_ratio_funcs():
    return list(ratio_funcs)


@pytest.fixture
def results_first(default_models_first_order):
    return {
        k: val.get("value")
        for k, val in default_models_first_order[
            "5peaks"
        ].lmfit_model.param_hints.items()
        if "value" in val
    }


@pytest.fixture
def results_second(default_models_second_order):
    return {
        k: val.get("value")
        for k, val in default_models_second_order[
            "2nd_4peaks"
        ].lmfit_model.param_hints.items()
        if "value" in val
    }


def test_calculate_params_keyerror(list_of_ratio_funcs, results_first):
    var_name = "no_var"
    with pytest.raises(KeyError):
        list_of_ratio_funcs[0](results_first, var_name)


def test_calculate_params_from_results(
    results_first, results_second, list_of_ratio_funcs
):
    combined_results = {**results_first, **results_second}

    prefix = ""
    var_name = "center"

    results = {}
    for ratio_func in list_of_ratio_funcs:
        label, ratio = ratio_func(combined_results, var_name, prefix=prefix)

        func = ratio_func.__name__
        results[func] = {"label": label, "ratio": ratio}
    assert results
    assert results["ratio_d_to_g"]["ratio"] < 1
    assert results["ratio_d_to_g"]["label"] == "D/G"
    for k, val in results.items():
        assert val["label"]
        assert val["ratio"] > 0
