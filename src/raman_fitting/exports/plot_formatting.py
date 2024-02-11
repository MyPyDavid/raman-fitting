#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 15:08:26 2021

@author: zmg
"""

from collections import namedtuple
from typing import Tuple

from raman_fitting.models.splitter import WindowNames

import matplotlib.pyplot as plt

from loguru import logger


CMAP_OPTIONS_DEFAULT = ("Dark2", "tab20")
DEFAULT_COLOR = (0.4, 0.4, 0.4, 1.0)
COLOR_BLACK = (0, 0, 0, 1)  # black as fallback default color

ModelValidation = namedtuple("ModelValidation", "valid peak_group model_inst message")


PLOT_WINDOW_AXES = {
    WindowNames.full: (0, 0),
    WindowNames.low: (0, 1),
    WindowNames.first_order: (0, 2),
    WindowNames.mid: (1, 1),
    WindowNames.second_order: (1, 2),
    WindowNames.normalization: (1, 0),
}


class PeakValidationWarning(UserWarning):
    pass


class NotFoundAnyModelsWarning(PeakValidationWarning):
    pass


class CanNotInitializeModelWarning(PeakValidationWarning):
    pass


def get_cmap_list(
    length: int,
    cmap_options: Tuple = CMAP_OPTIONS_DEFAULT,
    default_color: Tuple = DEFAULT_COLOR,
) -> Tuple:
    lst = list(range(length))
    if not lst:
        return None

    # set fallback color from class
    if isinstance(default_color, tuple) and default_color is not None:
        if len(default_color) == 4:
            cmap = [default_color for i in lst]
    elif default_color is None:
        cmap = [DEFAULT_COLOR for i in lst]
    else:
        raise ValueError(f"default color is not tuple but {type(default_color)}")

    # set cmap colors from cmap options
    if cmap_options:
        try:
            pltcmaps = [plt.get_cmap(cmap) for cmap in cmap_options]
            # Take shortest colormap but not
            cmap = min(
                [i for i in pltcmaps if len(lst) <= len(i.colors)],
                key=lambda x: len(x.colors),
                default=cmap,
            )
            # if succesfull
            if "ListedColormap" in str(type(cmap)):
                cmap = cmap.colors

        except Exception as exc:
            logger.warning(f"get_cmap_list error setting cmap colors:{exc}")

    return cmap


def assign_colors_to_peaks(selected_models: list) -> dict:
    cmap_get = get_cmap_list(len(selected_models))
    annotated_models = {}
    for n, peak in enumerate(selected_models):
        color = ", ".join([str(i) for i in cmap_get[n]])
        lenpars = len(peak.param_names)
        res = {"index": n, "color": color, "lenpars": lenpars, "peak": peak}
        annotated_models[peak.prefix] = res
    return annotated_models


def __repr__(self):
    _repr = "Validated Peak model collection"
    if self.selected_models:
        _selmods = f", {len(self.selected_models)} models from: " + "\n\t- "
        _repr += _selmods
        _joinmods = "\n\t- ".join(
            [f"{i.peak_group}: {i.model_inst} \t" for i in self.selected_models]
        )
        _repr += _joinmods
    else:
        _repr += ", empty selected models"
    return _repr
