# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 12:05:19 2020

@author: DWXMG
"""
from os import cpu_count
from multiprocessing import Pool
from functools import partial
#from .fit_models import Fit_1stOrder_Carbon


if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))
    from FileHelper import FindExpFolder,SampleIDstr,FindSampleID
    from RAMANpy.indexer import OrganizeRamanFiles
    from RAMANpy.fit_models import NormalizeFit, start_fitting, Fit_1stOrder_Carbon
#    from RAMANpy.fit_models import FittingLoop_1stOrder, FittingLoop_2ndOrder
    from RAMANpy.plotting import raw_data_export, fit_spectrum_plot
    
else:
    sys.path.append(str(Path(__file__).parent.parent))
    from FileHelper import FindExpFolder,SampleIDstr,FindSampleID

def worker_wrapper(arg):
    args, kwargs = arg
    return worker(*args, **kwargs)

def compute_desc_pool(coord, radius, coords, feat, verbose):    
    compute_desc(coord, radius, coords, feat, verbose)

def f(args,kwargs):
    return *args,**kwargs
    
results = run_fitting_multi(x,y,export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col, model_options = model_option)

def run_fitting_multi(x,y,export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col, model_options = model_option):
    return 
    
def fit_peak(peak_model,*args,**kwargs):
    Fit_1stOrder_Carbon(args,peak_model = peak_model, kwargs)
    
def multi_fit(x,y,peak_model = peak_model, export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col):
     Fit_1stOrder_Carbon(x,y,peak_model = peak_model, export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col)

start_fitting(fitting_specs)
def run_multi_fitting(peak_model,*args,**kwargs):
    
    for peak_model in model_options:
        FittingComps, FittingParams, FitReport = Fit_1stOrder_Carbon(x,y,peak_model = peak_model, 
                                                          export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col)
        Result_peak = Result_peak_nt(FittingComps, FittingParams, info_spec_1st, peak_model, spec_1st.sIDmean_col, FitReport)
        results.update({peak_model : Result_peak})
        


if __name__ == '__main__':
    with Pool(cpu_count()-2) as pool:
         try:
             results = run_multi_fitting(peak_model,)
             pool.map(run_multi_fitting(peak_model,), par_files_run)
         except Exception as e:
             print('FileHelper module not found:',e)
             logger.error('Classifier multiprocessing error: {0}'.format(e))
             results = pool.map(EC_classifier_multi_core.EC_PAR_file_check, par_files_run)
        
        
    
    with Pool(5) as p:
        print(p.map(f, [1, 2, 3]))
        
        
            
        with multiprocessing.Pool(os.cpu_count()-2) as pool:
            try:
                results = pool.map(EC_classifier_multi_core.EC_PAR_file_check, par_files_run)
            except Exception as e:
                print('FileHelper module not found:',e)
                logger.error('Classifier multiprocessing error: {0}'.format(e))
                results = pool.map(EC_classifier_multi_core.EC_PAR_file_check, par_files_run)
        out = pd.DataFrame(results)