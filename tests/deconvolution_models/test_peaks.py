#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:00:57 2021

@author: zmg
"""
from raman_fitting.deconvolution_models import first_order_peaks
from raman_fitting.deconvolution_models.base_peak import BasePeak






class test_peak(BasePeak):
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='test', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
    
    def input_param_settings(self):
        # TODO maybe read in param settings form eg xls file
        param_settings = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        param_settings = {}
        return param_settings
    
    def normalization_param_settings(self):
        settings = {'center' : {'value' : 1581, 'min' : 1500, 'max' : 1600},
                    'sigma' : {'value' : 40, 'min' : 1E-05, 'max' : 1E3},
                    'amplitude' : {'value' : 8E4, 'min' : 1E2}}
        return settings


class test_peak2(BasePeak):
    
    def __init__(self, peak_type = 'Gaussian', peak_name ='t2', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
    
    def input_param_settings(self):
        # TODO maybe read in param settings form eg xls file
        param_settings = {'center' : {'value' : 1271,'min' : 1245, 'max' : 1295},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        param_settings = {}
        return param_settings
    
    def normalization_param_settings(self):
        settings = {'center' : {'value' : 1281, 'min' : 1100, 'max' : 1600},
                    'sigma' : {'value' : 42, 'min' : 1E-05, 'max' : 1E3},
                    'amplitude' : {'value' : 8E4, 'min' : 1E2}}
        return settings




def _test_add():
    bp1 = test_peak()
    bp2 = test_peak2()
    bp1+bp2


def _testing():
    bp = BasePeak()
    bp.peak_type = 'Cheese' # error
    bp.peak_type = 'Voigt'
    
    bp.peak_name = 'pre'*100 # error
    bp.model.name
    
    # updating name and model
    bp.peak_name = 'G'
    bp.model.name
    bp.peak_type = 'Lorentzian'
    bp.model.name
    
    help(bp)

def _testing_class(classname):
    bp = classname()
    try:
        bp.peak_type = 'Cheese' # error
    except Exception as e:
        print('Error 1:', e)
    bp.peak_type = 'Voigt'
    
    try:
        bp.peak_name = 'pre'*100 # error
    except Exception as e:
        print('Error 2:', e)
    bp.model.name
    
    # updating name and model
    bp.peak_name = 'G'
    print(f'Model name: {bp.model.name}')
    bp.peak_type = 'Lorentzian'
    print(f'Model name: {bp.model.name}')
    bp.model.name
    return bp 
    
def _testing_func():
    bp = _testing_class(test_peak)
    
    bp2 = _testing_class(test_peak(peak_name='ADD'))




    
def _testing():
    Gp = first_order_peaks.G_peak()
    Gp
    Gp.print_params()
    tp = test_peak()
    
    model = G_peak() + D_peak()