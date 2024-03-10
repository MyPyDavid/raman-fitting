from typing import Tuple, List, Dict
from functools import wraps

from raman_fitting.utils.decorators import decorator_with_kwargs
from raman_fitting.utils.string_operations import join_prefix_suffix


def validate_result(result, var_name: str, requires: List[str] | None = None):
    req_vars = {join_prefix_suffix(i, var_name) for i in requires}
    provided_vars = {join_prefix_suffix(i, var_name) for i in result.keys()}
    if provided_vars < req_vars:
        raise ValueError(
            f"Missing required vars {req_vars} in result: {', '.join(result.keys())}"
        )


@decorator_with_kwargs
def calculate_ratio(function, requires: List[str] | None = None):
    @wraps(function)
    def wrapper(result, var_name: str, prefix: str | None = None, **kwargs):
        validate_result(result, var_name, requires=requires)
        prefix = prefix or ""
        return function(result, var_name, prefix=prefix)

    return wrapper


def get_var(peak: str, result: Dict, var_name: str):
    return result[join_prefix_suffix(peak.upper(), var_name)]


@calculate_ratio(requires=["D", "G"])
def ratio_d_to_g(result, var_name: str, prefix: str | None = None) -> Tuple[str, float]:
    d_ = get_var("D", result, var_name)
    g_ = get_var("G", result, var_name)
    ratio = d_ / g_
    label = f"{prefix}D/{prefix}G"
    return label, ratio


@calculate_ratio(requires=["D", "G"])
def ratio_la_d_to_g(
    result, var_name: str, prefix: str | None = None
) -> Tuple[str, float]:
    ratio = 4.4 * (ratio_d_to_g(result, var_name, prefix=prefix)[-1]) ** -1
    label = f"La_{prefix}G"
    return label, ratio


@calculate_ratio(requires=["D", "G", "D2"])
def ratio_d_to_gplusd2(
    result, var_name: str, prefix: str | None = None
) -> Tuple[str, float] | None:
    d = get_var("D", result, var_name)
    g = get_var("G", result, var_name)
    d2 = get_var("D2", result, var_name)
    ratio = d / (g + d2)
    label = f"{prefix}D/({prefix}G+{prefix}D2)"
    return label, ratio


@calculate_ratio(requires=["D", "G", "D2"])
def ratio_la_d_to_gplusd2(
    result, var_name: str, prefix: str | None = None
) -> Tuple[str, float]:
    ratio = 4.4 * (ratio_d_to_gplusd2(result, var_name, prefix=prefix)[-1]) ** -1
    label = (f"La_{prefix}G+D2",)
    return label, ratio


@calculate_ratio(requires=["D2", "G", "D3"])
def ratio_d3_to_gplusd2(
    result, var_name: str, prefix: str | None = None
) -> Tuple[str, float] | None:
    d2 = get_var("D2", result, var_name)
    d3 = get_var("D3", result, var_name)
    g = get_var("G", result, var_name)
    ratio = d3 / (g + d2)
    label = f"{prefix}D3/({prefix}G+{prefix}D2"
    return label, ratio


@calculate_ratio(requires=["D3", "G"])
def ratio_d3_to_g(
    result, var_name: str, prefix: str | None = None
) -> Tuple[str, float] | None:
    d3 = get_var("D3", result, var_name)
    g = get_var("G", result, var_name)
    ratio = d3 / g
    label = f"{prefix}D3/{prefix}G"
    return label, ratio


@calculate_ratio(requires=["D4", "G"])
def ratio_d4_to_g(
    result, var_name: str, prefix: str | None = None
) -> Tuple[str, float] | None:
    d4 = get_var("D4", result, var_name)
    g = get_var("G", result, var_name)
    ratio = d4 / g
    label = f"{prefix}D4/{prefix}G"
    return label, ratio


@calculate_ratio(requires=["D1D1", "D"])
def ratio_d1d1_to_d(result, var_name: str, prefix: str | None = None):
    d1d1 = get_var("D1D1", result, var_name)
    d = get_var("D", result, var_name)
    ratio = 8.8 * d1d1 / d
    label = f"Leq_{prefix}"
    return label, ratio


@calculate_ratio(requires=["D1D1", "GD1"])
def ratio_d1d1_to_gd1(
    result, var_name: str, prefix: str | None = None
) -> Tuple[str, float]:
    d1d1 = get_var("D1D1", result, var_name)
    gd1 = get_var("GD1", result, var_name)
    ratio = d1d1 / gd1
    label = f"{prefix}D1D1/{prefix}GD1"

    return label, ratio


if __name__ == "__main__":
    result = {"D_peak": 1, "G_peak": 2, "D1D1_peak": 3}
    var_name = "peak"
    print(ratio_d_to_g(result, var_name))
