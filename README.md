[![CI GH actions](https://github.com/MyPyDavid/raman-fitting/actions/workflows/build-test-codecov.yml/badge.svg)](https://github.com/MyPyDavid/raman-fitting/actions/workflows/build-test-codecov.yml)
[![codecov](https://codecov.io/gh/MyPyDavid/raman-fitting/branch/main/graph/badge.svg?token=II9JZAODJY)](https://codecov.io/gh/MyPyDavid/raman-fitting)
[![Test & Upload to TestPyPI](https://github.com/MyPyDavid/raman-fitting/actions/workflows/upload-to-testpypi.yml/badge.svg)](https://github.com/MyPyDavid/raman-fitting/actions/workflows/upload-to-testpypi.yml)


# raman-fitting
 A Python framework that performs a deconvolution on typical parts of interest on the spectrum of carbonaceous materials.
 The deconvolutions are done with models which are composed of collections of lineshapes or peaks that are typically assigned to these spectra in scientific literature.




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
python -m pip install raman-fitting/

# editable/develop mode
python -m pip install -e raman-fitting/
```

### Usage

#### Post installation test run 

In order to test the package after installation, please try the following cli command in a terminal
``` bash
raman_fitting -M make_examples
```
or these commands in the python interpreter.
``` python
import raman_fitting
raman_fitting.make_examples()
```
This test run should yield the resulting plots and files in the following folder. Where home means the local user home directory depending on the OS.
``` bash
home/.raman_fitting/example_results
```

#### Fitting your own datafiles
Place your data files in the default location or change this default setting in the config.
``` bash
home/.raman_fitting/datafiles
```
The following command will attempt the indexing, preprocessing, fitting and plottig on all the files found in this folder.
``` bash
# default run mode is "normal" means over all the files found in the index
raman_fitting

# If you add a lot of files, try to check if the index is properly constructed
before fitting them.
raman_fitting -M make_index 

# Location of index
home/.raman_fitting/datafiles/results/raman_fitting_index.csv
```

#### Datafiles

The raman data files should be .txt files with two columns of data values.
The first column should contain the Raman shift values and the second one the measured intensity.
Filenames will be parsed into a sampleID and position, in order to take the mean of the measured intensity 
of several positions on the same sample.

An example of filename formatting and parsing result:
``` python
samplename1_pos1.txt => sampleID = 'samplename1', position = 1
sample2-100_3.txt => sampleID = 'sample2-100', position = 3
```
### Version

The current version is v0.6.9

### Dependencies

- python >= 3.7
- lmfit >= 1.0.0
- pandas >= 1.0.5
- scipy >= 1.4.1
- matplotlib >= 3.1.2
- numpy >= 1.19.2
