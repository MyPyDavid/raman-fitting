# raman-fitting
These modules will index raman data files in a chosen folder and perform a fitting on typical parts of interest on the spectrum of carbonaceous materials.

First, it will try to extract a sample ID and position number from the filenames and create an index of the files in a dataframe. Over this index a preprocessing, fitting and exporting loop will start.
There are several models, each with a different combination of typical peaks, used for fitting. Each individual typical peak is defined as a class in the fit_models.py file with some added literature reference. Here, the individual peaks can also be easily adjusted for initial values, limits, shape (eg. Lorentzian, Gaussian and Voigt) or be fixed on initial values.
Export is done with plots and excel files for the spectral data and fitting parameters for further analysis.


### Example plots

https://github.com/MyPyDavid/raman-fitting/wiki


### Installation

Please install the package from this source, installation from PyPI will follow soon.
These command are based on a linux terminal.

- Download or clone this repository in a certain folder:
'git clone https://github.com/MyPyDavid/raman-fitting.git'

- Set up a virtual environment for python:
'python -m venv testenv'

- Activate the virtual environment:
'source /testenv/bin/activate'

- Install the repository from the folder wherein the repo was cloned. The required dependencies should be installed as well:
'pip install -e raman-fitting'

- Testing the package after installation:
     via the cli command:
        'raman_fitting -M make_examples'
    via python interpreter api:
        '>>> import raman_fitting'
        '>>> raman_fitting.make_examples()'


### Dependencies

- python >= 3.7
- lmfit >= 1.0.0
- pandas >= 1.0.5
- scipy >= 1.4.1
- matplotlib >= 3.1.2
- numpy >= 1.19.2
