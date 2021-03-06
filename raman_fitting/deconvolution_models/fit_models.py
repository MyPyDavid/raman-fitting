#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:51:17 2020

@author: DW
"""

from collections import OrderedDict,namedtuple

import datetime as dt
import pandas as pd

from raman_fitting.deconvolution_models.base_model import InitializeModels


def _testing():
    ft = Fitter(spectra_collection)
    ft.fit_delegator()
    self = ft
    
    self = prep


class Fitter:
    
    fit_windows = ['1st_order', '2nd_order']
    
    def __init__(self, spectra_arg, RamanModels = InitializeModels(), start_fit = True):
        self.start_fit = start_fit
        self.models = RamanModels
        
        self.spectra_arg = spectra_arg
        self.spectra = spectra_arg
        self.fit_delegator()
        
    @property
    def spectra(self):
        return self._spectra
    
    @spectra.setter
    def spectra(self, value):
        
        _errtxt = (f'This assignment {value} does not contain valid spectra')
        
        if type(value) == dict:
            _data = value
        elif type(value).__name__ == 'SpectrumDataCollection':
            _data = value.mean_data
            _fit_lbl = 'mean'
        elif type(value).__name__ == 'SpectrumDataLoader':
            _data = value.clean_df
            _fit_lbl = 'int'
        elif type(value) == pd.DataFrame:
            raise AttributeError
            self.sense_windowname(value)
        else:
            raise ValueError(_errtxt)
            
        _specs = {k:val for k,val in _data.items() if k in self.fit_windows and type(val) == pd.DataFrame}
        assert bool(_specs), _errtxt
        self._spectra = _specs
        self.FitResults = {}
        self.info = {}
        if hasattr(value, 'info'):
            self.info = {**self.info, **value.info}
    
    def fit_delegator(self):
        
        if self.start_fit:
            self.fit_models(self.models.second_order)
            self.fit_models(self.models.first_order)
            
    def fit_models(self, model_selection):
        
        _fittings = {}
        for modname, model in model_selection.items():
            modname, model 
            _windowname = [i for i in self.fit_windows if modname[0:3] in i][0]
            _data = self.spectra.get(_windowname)
            _int_lbl = self.get_int_label(_data)
            
            out = self.run_fit(model, _data, _int_lbl = _int_lbl, _modelname = modname, _info = self.info)
            prep = PrepareParams(out, extra_fit_results = self.FitResults)
            _fittings.update({modname : prep.FitResult})
        self.FitResults.update(**_fittings)
            
    def run_fit(self, model, _data, **kws):
        _fit_res, _param_res = {}, {}
        init_params = model.model.make_params()
        x, y = _data.ramanshift, _data[kws.get('_int_lbl')]
        out = model.model.fit(y,init_params,x=x,method='leastsq') # 'leastsq'
        for k,val in kws.items():
            setattr(out,k,val)
        return out
    
    def get_int_label(self, value):
        cols = [i for i in value.columns if not 'ramanshift' in i]
        if len(cols) == 0:
            _lbl = ''
        if len(cols) == 1:
            _lbl = cols[0]
        elif len(cols) > 1:
            if any('mean' in i for i in cols):
                _lbl = [i for i in cols if 'mean' in i][0]
            elif any('int' in i for i in cols):
                _lbl = [i for i in cols if 'int' in i][0]
            else:
                _lbl =''
        return _lbl        
     

class PrepareParams:
    
    fit_attr_export_lst = ('chisqr','redchi','bic','aic', 'method','message','success','nfev')
    fit_result_template = namedtuple('FitResult', ['FitComponents','FitParameters', 'FitReport',
                                                    'extrainfo','model_name', 'raw_data_col'])
    ratio_params = [('I','_height'), ('A','_amplitude')]
    _standard_2nd_order = '2nd_4peaks'
    
    def __init__(self, model_result, extra_fit_results =  {}):
        self.extra_fit_results = extra_fit_results
        self.model_result = model_result
    
    
    @property
    def model_result(self):
        return self._model_result
    
    @model_result.setter
    def model_result(self, value):
        ''' 
        Takes the ModelResult class instance from lmfit.
        Optional extra functionality with a list of instances.
        '''
        
        self.result = {}
        
        if 'ModelResult' in type(value).__name__:
            self.result.update(value.params.valuesdict())
            self.comps = value.model.components
            
        elif ('list' or 'tuple') in type(value).__name__:
            assert all('ModelResult' in type(i).__name__ for i in value)
            [self.result.update(mod.params.valuesdict()) for mod in value]
            self.comps = [i for mod in value for i in mod.model.components]
            
        self.peaks = set([i.prefix for i in self.comps]) # peaks is prefix from components
            
        _mod_lbl = 'Model'
        if hasattr(value,'_modelname'):
            _mod_lbl = f'Model_{getattr(value,"_modelname")}'
        self.model_name_lbl = _mod_lbl    
        
        self.raw_data_lbl = value.data.name
        
        self._model_result = value
        
        self.make_result()
    
    def make_result(self):
        
        self.prep_params()
        self.prep_components()
        self.FitReport = self.model_result.fit_report(show_correl=False)
        self.prep_extra_info()
        
        self.FitResult = self.fit_result_template(self.FitComponents,self.FitParameters, self.FitReport, 
                                                  self.extra_info, self.model_name_lbl, self.raw_data_lbl)
    
    def prep_extra_info(self):
        self.extra_info = {}
        _destfitcomps = self.model_result._info['DestFittingComps']
        _model_destdir = _destfitcomps.joinpath(f'{self.model_name_lbl}_{self.model_result._info["SampleID"]}')
        self.extra_info = {**self.model_result._info, **{'DestFittingModel' : _model_destdir}}
    
    def prep_params(self):
        fit_attrs = OrderedDict(zip([f'lmfit_{i}' for i in self.fit_attr_export_lst],
                                    [getattr(self.model_result,i) for i in self.fit_attr_export_lst]))
        self.result.update(fit_attrs)
        try:
            self.add_ratio_params()
        except Exception as e:
            print(e)
            
        self.result.update({'_run_date_YmdH' : dt.datetime.now().strftime(format='%Y-%m-%d %H:00')})
        self.FitParameters = pd.DataFrame(self.result,index=[self.model_name_lbl])
        
    def add_ratio_params(self):
        # peaks = [i.prefix for i in self.out.model.components]
        
        RatioParams = {}
        for a,t in self.ratio_params:
            if {'G_', 'D_'}.issubset(self.peaks):
                RatioParams.update({f'{a}D/{a}G' : self.result['D'+t]/self.result['G'+t]})
                RatioParams.update({f'La_{a}G' : 4.4*RatioParams.get(f'{a}D/{a}G')**-1})
    #                , 'ID/IG' : fit_params_od['D_height']/fit_params_od['G_height']}
                if 'D2_' in self.peaks:
                    RatioParams.update({f'{a}D/({a}G+{a}D2)' : self.result['D'+t]/(self.result['G'+t]+self.result['D2'+t])})
                    RatioParams.update({f'La_{a}G+D2' : 4.4*RatioParams.get(f'{a}D/({a}G+{a}D2)')**-1})
    #               : fit_params_od['D'+t]/(fit_params_od['G'+t]+fit_params_od['D2'+t])})
                    if 'D3_' in self.peaks:
                        RatioParams.update({f'{a}D3/({a}G+{a}D2' : self.result['D3'+t]/(self.result['G'+t]+self.result['D2'+t])})
            if 'D3_' in self.peaks:
                    RatioParams.update({f'{a}D3/{a}G' : self.result['D3'+t]/self.result['G'+t]})
            if 'D4_' in self.peaks:
                RatioParams.update({f'{a}D4/{a}G' : self.result['D4'+t]/self.result['G'+t]})
            
            if {'D1D1_','GD1_'}.issubset(self.peaks):
                    RatioParams.update({f'{a}D1D1/{a}GD1' : self.result['D1D1'+t]/self.result['GD1'+t]})
            if self.extra_fit_results:
                RatioParams.update(self.add_ratio_combined_params( a, t))
                
        self.ratio_params = RatioParams
        self.result.update(RatioParams)
        
    def add_ratio_combined_params(self, a, t):
        
        _2nd = self._standard_2nd_order
        if self.model_result._modelname.startswith('1st') and _2nd in self.extra_fit_results.keys():
            _D1D1 = self.extra_fit_results[_2nd].FitParameters.loc[f'Model_{_2nd}', 'D1D1'+t]
            self.result.update({'D1D1'+t : _D1D1})
            return {f'Leq_{a}' : 8.8 * _D1D1 / self.result['D'+t]}
        else:
            return {}
    
    def prep_components(self):
        # FittingParams = pd.DataFrame(fit_params_od,index=[peak_model])
        _fit_comps_data = OrderedDict({'RamanShift' : self.model_result.userkws['x']})
    
        _fit_comps_data.update(self.model_result.eval_components())
       
        _fit_comps_data.update({self.model_name_lbl : self.model_result.best_fit, 'residuals' :  self.model_result.residual, 
                                self.model_result.data.name : self.model_result.data})
        FittingComps = pd.DataFrame(_fit_comps_data)
        self.FitComponents = FittingComps
        


def NormalizeFit(norm_cleaner,plotprint = False): # TODO optional add normalization seperately to Fitter
    x,y = norm_cleaner.spec.ramanshift, norm_cleaner.blcorr_desp_intensity
    Model = ModelChoices('2peaks normalization Lorentzian')
    params = Model.make_params()
    pre_fit = Model.fit(y,params ,x=x) # 'leastsq'
    IG,ID = pre_fit.params['G_height'].value, pre_fit.params['D_height'].value
    output = {'factor' : 1/IG, 'ID/IG' : ID/IG, 'ID' : ID,'IG' : IG, 
              'G_center' : pre_fit.params['G_center'].value, 'D_center' : pre_fit.params['D_center'].value, 'Model' : Model}
#    pre_fit = Model.fit(y,params ,x=x,method='differential-evolution') # 'leastsq'
    if plotprint:
        pre_fit.plot() 
        print(pre_fit.fit_report())
    return output
