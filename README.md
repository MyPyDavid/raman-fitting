# raman-fitting
 A Python framework that performs a deconvolution on typical parts of interest on the spectrum of carbonaceous materials.
 The deconvolutions are done with models which are composed of collections of lineshapes or peaks that typically assigned to these spectra in scientific literature.




In batch processing mode this framework will index raman data files in a chosen folder.
First, it will try to extract a sample ID and position number from the filenames and create an index of the files in a dataframe. Over this index a preprocessing, fitting and exporting loop will start.
There are several models, each with a different combination of typical peaks, used for fitting. Each individual typical peak is defined as a class in the fit_models.py file with some added literature reference. Here, the individual peaks can also be easily adjusted for initial values, limits, shape (eg. Lorentzian, Gaussian and Voigt) or be fixed on initial values.
Export is done with plots and excel files for the spectral data and fitting parameters for further analysis.


### Example plots

https://github.com/MyPyDavid/raman-fitting/wiki


### Installation

Please install the package from this source, installation from PyPI will follow soon.
The following commands for installation and testing are based on a linux terminal.

Download or clone this repository in a certain folder.
``` bash
git clone https://github.com/MyPyDavid/raman-fitting.git
```
Set up a virtual environment for python.
``` bash
python -m venv testenv
```
Activate the virtual environment.
``` bash
source /testenv/bin/activate
```
Install the repository from the folder wherein the repo was cloned or downloaded.
The required dependencies should be installed automatically as well.
``` bash
# regular install
pip install raman-fitting/

# develop mode
pip install -e raman-fitting/
```
Test the package after installation with the following cli command.
``` bash
raman_fitting -M make_examples
```
Test the package after installation in the python interpreter with the api commands.
``` python
import raman_fitting
raman_fitting.make_examples()
```

### Dependencies

- python >= 3.7
- lmfit >= 1.0.0
- pandas >= 1.0.5
- scipy >= 1.4.1
- matplotlib >= 3.1.2
- numpy >= 1.19.2
