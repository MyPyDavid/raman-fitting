# -*- coding: utf-8 -*-
import textwrap

from setuptools import setup

setup(
    use_scm_version={
        "write_to": "src/raman_fitting/_version.py",
        "write_to_template": textwrap.dedent(
            """
             # coding: utf-8
             from __future__ import unicode_literals
             __version__ = {version!r}
             """,
        ).lstrip(),
    },
    package_dir={"": "src"},
)
