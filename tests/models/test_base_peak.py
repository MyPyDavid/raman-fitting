from raman_fitting.models.deconvolution.base_peak import BasePeak


def test_initialize_base_peaks(
    default_definitions, default_models_first_order, default_models_second_order
):
    peaks = {}

    peak_items = {
        **default_definitions["first_order"]["peaks"],
        **default_definitions["second_order"]["peaks"],
    }.items()
    for k, v in peak_items:
        peaks.update({k: BasePeak(**v)})

    peak_d = BasePeak(**default_definitions["first_order"]["peaks"]["D"])
    assert (
        peak_d.peak_name
        == default_definitions["first_order"]["peaks"]["D"]["peak_name"]
    )
    assert (
        peak_d.peak_type
        == default_definitions["first_order"]["peaks"]["D"]["peak_type"]
    )
    assert (
        peak_d.lmfit_model.components[0].prefix
        == default_definitions["first_order"]["peaks"]["D"]["peak_name"] + "_"
    )
    assert (
        peak_d.param_hints["center"].value
        == default_definitions["first_order"]["peaks"]["D"]["param_hints"]["center"][
            "value"
        ]
    )
