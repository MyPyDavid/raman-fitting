from inspect import getmembers, isfunction
from typing import Dict

from raman_fitting.models.post_deconvolution import parameter_ratio_funcs

functions = [
    fn
    for _, fn in getmembers(parameter_ratio_funcs, isfunction)
    if fn.__module__ == parameter_ratio_funcs.__name__
]
ratio_funcs = filter(lambda x: x.__name__.startswith("ratio_"), functions)


def calculate_params_from_results(
    result_first: Dict, result_second: Dict, prefix: str, var_name: str
):
    combined_results = {**result_first, **result_second}
    ret = {}
    for ratio_func in ratio_funcs:
        _ratio = dict(ratio_func(combined_results, prefix, var_name))
        ret.update(_ratio)
    return ret


def main():
    print(functions)
    print(list(map(str, ratio_funcs)))


if __name__ == "__main__":
    main()
