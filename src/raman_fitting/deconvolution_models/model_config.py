"""
Created on Sun May 30 12:35:58 2021

@author: DW
"""

from raman_fitting.model_validation import PeakModelValidator


class ModelConfigurator:
    standard_config_file = "model_config_standard.cfg"

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def find_user_config_files(self):
        pass

    def file_handler(self):
        pass

    def standard_valid_models(self):
        peak_collection = PeakModelValidator()
