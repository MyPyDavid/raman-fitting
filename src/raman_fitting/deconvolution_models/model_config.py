"""
Created on Sun May 30 12:35:58 2021

@author: DW
"""
if __name__ == '__main__':
    from model_validation import PeakModelValidator
    from raman_fitting.config.config import PACKAGE_HOME
    
else:
    from model_validation import PeakModelValidator
    from ..config.config import PACKAGE_HOME



class ModelConfigurator():
    
    standard_config_file = 'modelconfig_standard'
    
    def __init__(self,**kwargs):
        self._kwargs = kwargs
        
        
    def standard_valid_models(self):
        
        peak_collection = PeakModelValidator()
        