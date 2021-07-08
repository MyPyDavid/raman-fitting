# -*- coding: utf-8 -*-
import textwrap

from setuptools import setup

# all settings for setup are in setup.cfg
setup(
    use_scm_version=True,
    setup_requires=["setuptools_scm", "setuptools_scm_git_archive"],
)
# package_dir={"": "src"},
# )

# "write_to_template": textwrap.dedent(
#             """
#              # coding: utf-8
#              from __future__ import unicode_literals
#              __version__ = {version!r}
#              """,
#         ).lstrip(),
