from typing import Dict, Tuple
from functools import wraps


def calculate_ratio(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        return f(*args, **kwds)

    return wrapper


@calculate_ratio
def ratio_d_to_g(result, prefix: str, var_name: str) -> Tuple[str, float]:
    return f"{prefix}D/{prefix}G", result["D" + var_name] / result["G" + var_name]


@calculate_ratio
def ratio_la_d_to_g(result, prefix: str, var_name: str) -> Dict:
    return f"La_{prefix}G", 4.4 * (ratio_d_to_g(result, prefix, var_name)) ** -1


@calculate_ratio
def ratio_d_to_gplusd2(result, prefix: str, var_name: str) -> Dict:
    if "D2" + var_name not in result:
        return
    return f"{prefix}D/({prefix}G+{prefix}D2)", result["D" + var_name] / (
        result["G" + var_name] + result["D2" + var_name]
    )


@calculate_ratio
def ratio_la_d_to_gplusd2(result, prefix: str, var_name: str) -> Dict:
    return f"La_{prefix}G+D2", 4.4 * (
        ratio_d_to_gplusd2(result, prefix, var_name)
    ) ** -1


@calculate_ratio
def ratio_d3_to_gplusd2(result, prefix: str, var_name: str) -> Dict:
    if "D3" + var_name not in result or "D2" + var_name not in result:
        return
    return f"{prefix}D3/({prefix}G+{prefix}D2", result["D3" + var_name] / (
        result["G" + var_name] + result["D2" + var_name]
    )


@calculate_ratio
def ratio_d3_to_g(result, prefix: str, var_name: str) -> Tuple[str, float]:
    if "D3" + var_name not in result:
        return
    return f"{prefix}D3/{prefix}G", result["D3" + var_name] / result["G" + var_name]


@calculate_ratio
def ratio_d4_to_g(result, prefix: str, var_name: str) -> Tuple[str, float]:
    if "D4" + var_name not in result:
        return
    return f"{prefix}D4/{prefix}G", result["D4" + var_name] / result["G" + var_name]


@calculate_ratio
def ratio_d1d1_to_d(result, prefix: str, var_name: str):
    if "D1D1" + var_name not in result:
        return
    return f"Leq_{prefix}", 8.8 * result["D1D1" + var_name] / result["D" + var_name]


@calculate_ratio
def ratio_d1d1_to_gd1(result, prefix: str, var_name: str) -> Tuple[str, float]:
    if "D1D1" + var_name not in result:
        return
    return f"{prefix}D1D1/{prefix}GD1", result["D1D1" + var_name] / result[
        "GD1" + var_name
    ]
