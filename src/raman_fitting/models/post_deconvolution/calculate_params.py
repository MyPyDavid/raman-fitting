from inspect import getmembers, isfunction
from typing import Dict, Any

from raman_fitting.models.post_deconvolution import parameter_ratio_funcs

RATIO_FUNC_PREFIX = "ratio_"
functions = [
    fn
    for _, fn in getmembers(parameter_ratio_funcs, isfunction)
    if fn.__module__ == parameter_ratio_funcs.__name__
]
ratio_funcs = list(
    filter(lambda x: x.__name__.startswith(RATIO_FUNC_PREFIX), functions)
)


def calculate_params_from_results(
    combined_results: Dict,
    var_name: str,
    prefix: str | None = None,
    raise_exception=True,
) -> dict[str, dict[str, Any]]:
    results = {}
    for ratio_func in ratio_funcs:
        try:
            label, ratio = ratio_func(combined_results, var_name, prefix=prefix)
            func = ratio_func.__name__
            results[func] = {"label": label, "ratio": ratio}
        except (ValueError, KeyError) as e:
            if raise_exception:
                raise e from e
            continue
    return results


def calculate_ratio_of_unique_vars_in_results(
    results: Dict, raise_exception: bool = True
) -> dict[Any, dict[str, dict[str, Any]]]:
    uniq_vars = set(i.split("_")[-1] for i in results.keys())
    var_ratios = {}
    for var_name in uniq_vars:
        ratios = calculate_params_from_results(
            results, var_name, raise_exception=raise_exception
        )
        var_ratios[var_name] = ratios
    return var_ratios


def main():
    print(functions)
    print(list(map(str, ratio_funcs)))


if __name__ == "__main__":
    main()
