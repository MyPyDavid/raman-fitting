# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for pytest and commonly used fixtures
"""
import importlib

import pandas
import pytest

# rname = importlib.util.resolve_name('raman_fitting', None)
# importlib.import_module('raman_fitting')
# print(f"pytest: {__name__},file: {__file__}\n name:")
# Incremental tests


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


# Global fixtures
