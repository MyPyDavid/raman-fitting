"""
Created on Mon Jul  5 21:48:10 2021

@author: DW

UNDER CONSTRUCTION

new design for the building of core spectra ojbects
# TODO implement
"""


class Spectrum:
    """
    Parent method for SingleSpectrum and MultiSpectrum classes
    """

    def check_data(self):
        """check if data is present"""

    def plot(self):
        """
        class method for child classes
        """
        pass

    def fit(self):
        """
        add all fitting properties and options
        """


class SingleSpectrum(Spectrum):
    def __init__(self, filename):
        """
        take filename and look up in the index or database
        """
        pass


class MeanSpectra(Spectrum):
    def __init__(self, sampleID=""):
        """
        take sampleID and look up in the index or database
        for the mean data of the different positions
        """
        pass


class MultiSpectra(Spectrum):
    def __init__(self, samples: list = []):
        """
        take sampleID and look up in the index or database
        for the mean data of the different positions
        """
        pass
