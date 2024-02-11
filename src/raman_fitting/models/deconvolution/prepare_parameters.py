from raman_fitting.models.splitter import WindowNames


#  TODO add params to run fit post processing
def add_D_G_ratios(a: str, t: str, peaks, result):
    RatioParams = {}
    if {"G_", "D_"}.issubset(peaks):
        RatioParams.update({f"{a}D/{a}G": result["D" + t] / result["G" + t]})
        RatioParams.update({f"La_{a}G": 4.4 * RatioParams.get(f"{a}D/{a}G") ** -1})
        #                , 'ID/IG' : fit_params_od['D_height']/fit_params_od['G_height']}
        if "D2_" in peaks:
            RatioParams.update(
                {
                    f"{a}D/({a}G+{a}D2)": result["D" + t]
                    / (result["G" + t] + result["D2" + t])
                }
            )
            RatioParams.update(
                {f"La_{a}G+D2": 4.4 * RatioParams.get(f"{a}D/({a}G+{a}D2)") ** -1}
            )
            #               : fit_params_od['D'+t]/(fit_params_od['G'+t]+fit_params_od['D2'+t])})
            if "D3_" in peaks:
                RatioParams.update(
                    {
                        f"{a}D3/({a}G+{a}D2": result["D3" + t]
                        / (result["G" + t] + result["D2" + t])
                    }
                )


def add_D3_ratio(a: str, t: str, peaks, result):
    RatioParams = {}
    if "D3_" in peaks:
        RatioParams.update({f"{a}D3/{a}G": result["D3" + t] / result["G" + t]})


def add_D4_ratio(a: str, t: str, peaks, result):
    RatioParams = {}
    if "D4_" in peaks:
        RatioParams.update({f"{a}D4/{a}G": result["D4" + t] / result["G" + t]})


def add_ratio_combined_params(
    windowname, a: str, t: str, result={}, extra_fit_results=None
):
    windowname_2nd = "2nd_4peaks"
    if windowname is None:
        return {}

    if windowname.startswith("first") and windowname_2nd in extra_fit_results.keys():
        _D1D1 = extra_fit_results[windowname_2nd].FitParameters.loc[
            f"Model_{windowname_2nd}", "D1D1" + t
        ]
        result.update({"D1D1" + t: _D1D1})
        return {f"Leq_{a}": 8.8 * _D1D1 / result["D" + t]}
    return {}


def add_D1D1_GD1_ratio(
    a: str, t: str, peaks, result, extra_fit_results, window_name=None
):
    RatioParams = {}
    if {"D1D1_", "GD1_"}.issubset(peaks):
        RatioParams.update({f"{a}D1D1/{a}GD1": result["D1D1" + t] / result["GD1" + t]})
    if extra_fit_results:
        RatioParams.update(add_ratio_combined_params(window_name, a, t))


def add_ratio_combined_params_second_order(
    result, model_result, extra_fit_results, a, t
):
    _2nd = WindowNames.second_order
    if model_result._modelname.startswith("first") and _2nd in extra_fit_results.keys():
        _D1D1 = extra_fit_results[_2nd].FitParameters.loc[f"Model_{_2nd}", "D1D1" + t]
        result.update({"D1D1" + t: _D1D1})
        return {f"Leq_{a}": 8.8 * _D1D1 / result["D" + t]}
    else:
        return {}
