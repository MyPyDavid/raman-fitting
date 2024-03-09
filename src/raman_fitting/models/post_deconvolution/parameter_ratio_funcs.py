from typing import Tuple, List
from functools import wraps

from raman_fitting.utils.decorators import decorator_with_kwargs
from raman_fitting.utils.string_operations import join_prefix_suffix

from loguru import logger


@decorator_with_kwargs
def calculate_ratio(function, requires: List[str] | None = None):
    @wraps(function)
    def wrapper(result, prefix: str, var_name: str, **kwargs):
        req_vars = {join_prefix_suffix(i, var_name) for i in requires}
        provided_vars = {join_prefix_suffix(i, var_name) for i in result.keys()}
        missing_req_vars = provided_vars - req_vars
        if missing_req_vars:
            logger.warning(
                f"Missing vars {missing_req_vars} in result: {', '.join(result.keys())}"
            )
            return
        return function(result, prefix, var_name, **kwargs)

    return wrapper


@calculate_ratio(requires=["G", "D"])
def ratio_d_to_g(result, prefix: str, var_name: str) -> Tuple[str, float]:
    return f"{prefix}D/{prefix}G", result["D" + var_name] / result["G" + var_name]


@calculate_ratio(requires=["G", "D"])
def ratio_la_d_to_g(result, prefix: str, var_name: str) -> Tuple[str, float]:
    return f"La_{prefix}G", 4.4 * (ratio_d_to_g(result, prefix, var_name)) ** -1


@calculate_ratio(requires=["D2", "G", "D"])
def ratio_d_to_gplusd2(result, prefix: str, var_name: str) -> Tuple[str, float] | None:
    return f"{prefix}D/({prefix}G+{prefix}D2)", result["D" + var_name] / (
        result["G" + var_name] + result["D2" + var_name]
    )


@calculate_ratio(requires=["D2", "G", "D"])
def ratio_la_d_to_gplusd2(result, prefix: str, var_name: str) -> Tuple[str, float]:
    return f"La_{prefix}G+D2", 4.4 * (
        ratio_d_to_gplusd2(result, prefix, var_name)
    ) ** -1


@calculate_ratio(requires=["D3", "D2", "G"])
def ratio_d3_to_gplusd2(result, prefix: str, var_name: str) -> Tuple[str, float] | None:
    return f"{prefix}D3/({prefix}G+{prefix}D2", result["D3" + var_name] / (
        result["G" + var_name] + result["D2" + var_name]
    )


@calculate_ratio(requires=["D3", "G"])
def ratio_d3_to_g(result, prefix: str, var_name: str) -> Tuple[str, float] | None:
    if "D3" + var_name not in result:
        return
    return f"{prefix}D3/{prefix}G", result["D3" + var_name] / result["G" + var_name]


@calculate_ratio(requires=["D4", "G"])
def ratio_d4_to_g(result, prefix: str, var_name: str) -> Tuple[str, float] | None:
    if "D4" + var_name not in result:
        return
    return f"{prefix}D4/{prefix}G", result["D4" + var_name] / result["G" + var_name]


@calculate_ratio(requires=["D1D1", "D"])
def ratio_d1d1_to_d(result, prefix: str, var_name: str):
    return f"Leq_{prefix}", 8.8 * result["D1D1" + var_name] / result["D" + var_name]


@calculate_ratio(requires=["D1D1", "GD1"])
def ratio_d1d1_to_gd1(result, prefix: str, var_name: str) -> Tuple[str, float]:
    return f"{prefix}D1D1/{prefix}GD1", result["D1D1" + var_name] / result[
        "GD1" + var_name
    ]


if __name__ == "__main__":
    result = {"D_peak": 1, "G_peak": 2, "D1D1_peak": 3}
    var_name = "peak"
    ratio_d_to_gplusd2(result, "", var_name)
