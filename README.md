# raman-fitting
These modules will index raman data files in a chosen folder and perform a fitting on typical parts of interest on the spectrum of carbonaceous materials. 

First, it will try to extract a sample ID and position number from the filenames and create an index of the files in a dataframe. Over this index a preprocessing, fitting and exporting loop will start.
There are several models, each with a different combination of typical peaks, used for fitting. Each individual typical peak is defined as a class in the fit_models.py file with some added literature reference. Here, the individual peaks can also be easily adjusted for initial values, limits, shape (eg. Lorentzian, Gaussian and Voigt) or be fixed on initial values.   
Export is done with plots and excel files for the spectral data and fitting parameters for further analysis.


### Example plots

https://github.com/MyPyDavid/raman-fitting/wiki


### Dependencies

- python >= 3.7 
- lmfit >= 1.0.0 
- pandas >= 1.0.5 
- scipy >= 1.4.1 
- matplotlib >= 3.1.2 
- numpy >= 1.19.2
