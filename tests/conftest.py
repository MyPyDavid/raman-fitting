# flake8: noqa
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for pytest and commonly used fixtures
"""
import pprint
import sys
import pathlib

# Need this for local editable install pytest run to work
# This pythonpath = "src" should have fixed it.
if "src" not in sys.path:
    sys.path.append("src")
    print("added src to sys.path")
    pprint.pprint(sys.path)
    pprint.pprint(pathlib.Path.cwd())


import raman_fitting

# Global fixtures
