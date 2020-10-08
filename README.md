# raman-fitting
These modules will index raman data files in a chosen folder and perform a fitting on typical parts of interest on the spectrum of carboneous materials.

First, it will try to extract a sample ID and position number from the filenames and index the filens in a dataframe. Over this index a preprocessing, fitting and exporting loop will start.
There are several models, each with a different number of peaks, used for fitting. Export is done with plots and excel files for the spectral data and fitting parameters for further analysis.

### Dependencies
python >= 3.7  
lmfit >= 1.0.0  
pandas >= 1.0.5  
scipy >= 1.4.1

### Example plot

https://github.com/MyPyDavid/raman-fitting/wiki
