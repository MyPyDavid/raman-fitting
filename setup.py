#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
from pathlib import Path

from setuptools import find_packages, setup


# Package meta-data.
NAME = 'raman_fitting'
DESCRIPTION = 'Package for the batch processing and deconvolution of raman spectra.'
URL = 'https://github.com/MyPyDavid/raman-fitting.git'
EMAIL = 'mypydavid@github.com'
AUTHOR = 'David Wallace'
REQUIRES_PYTHON = '>=3.7.0'

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the
# Trove Classifier for that!

# here = Path(__file__).parent
ROOT_DIR = Path(__file__).resolve().parent

# What packages are required for this module to be executed?
def _list_requirements(ROOT_DIR):
    _req_txt_filename = ROOT_DIR.joinpath('requirements.txt')
    try:
        _req_lst = _req_txt_filename.read_text().splitlines()
    except Exception as e:
        _err = f'No requirements.txt {e}'
        _req_lst = []
    return _req_lst


# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(ROOT_DIR.joinpath('README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


# Load the package's __version__.py module as a dictionary.

PACKAGE_DIR = ROOT_DIR / 'src' / NAME
about = {}
with open(PACKAGE_DIR / 'VERSION') as f:
    _version = f.read().strip()
    about['__version__'] = _version


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    project_urls={
        # "Documentation": 'https://.readthedocs.io', # TODO prepare readme docs
        "Source Code": URL,
    },
    packages=find_packages('src',
                           exclude=('tests',)),
    package_dir={'': 'src'},
    py_modules=[path.name.suffix for path
                in Path('./src').glob('*.py')],
    package_data={'': ['VERSION','datafiles/example_files/*.txt']},
    entry_points={
        'console_scripts': [
            f'{NAME} = {NAME}.cli:main'
        ]
    },
    install_requires=_list_requirements(ROOT_DIR),
    tests_require=['pytest'],
    extras_require={},
    include_package_data=True,
    license='MIT license',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
)

#  Other requirements for future version
# extras_require={
#         'dev': [
#             'isort',
#             'pylint',
#             'flake8',
#             'autopep8',
#             'pydocstyle',
#             'bump2version',
#         ],
#         'docs': [
#             'docutils >= 0.11'
#             'doc8',
#             'pandoc',
#             'restructuredtext-lint',
#             'sphinx',
#             'nbsphinx',
#             'sphinx_rtd_theme',
#         ],
#     }
