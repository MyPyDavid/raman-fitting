#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:51:17 2020

@author: DW
"""

from collections import OrderedDict,namedtuple
from typing import Iterable

import datetime as dt
import pandas as pd
# from lmfit.models import VoigtModel,LorentzianModel, GaussianModel

from raman_fitting.deconvolution_models.model_validation import Peak_Collection
# from .model_validation import Peak_Collection
# TODO split this module into the 1st and 2nd order related peaks



# ====== MODEL CHOICE ======= #


class BaseModel():
    ''' This Model class combines the peaks from BasePeak into a regression model 
        that is compatible with the lmfit Model and fit functions.
    '''
    
    model_prefix_name = ''
    
    def __init__(self, peak_collection = Peak_Collection(), model_name = '', add_substrate = True, substrate_peak = 'Si1_peak'):
        self.peak_collection = peak_collection
        self._model_name = model_name
        self._add_substrate = add_substrate
        self.substrate_peak = substrate_peak
        
        self.model_constructor()
        # self.peak_dict = self.peak_collection.get_dict()
        
    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, name):
        '''Calls the model constructer on the model_name'''
        self._model_name = name
        self.model_constructor()
    
    @property
    def add_substrate(self):
        return self._add_substrate
    
    @add_substrate.setter
    def add_substrate(self, value : bool):
        _hasattr_model = hasattr(self, 'model')
        if _hasattr_model and value:
            self.add_substrate_to_model()    
        elif _hasattr_model and not value:
            self.model_constructor()
            
        elif not _hasattr_model and value:
            self.model_constructor()
            self.add_substrate_to_model()
        else:
            self.model_constructor()
            
    def add_substrate_to_model(self):
        if hasattr(self,'model'):
            self.model_raw = self.model
            if not any([i.prefix[:-1] in self.substrate_peak for i in self.model.components]):
                self.model = self.model_raw + getattr(self.peak_collection, self.substrate_peak).model
        
    def model_constructor(self):
        
        if type(self._model_name) == str:
            _splitname = self._model_name.split('+')
            assert _splitname, f'Chose name for model is empty {self.name}'
            _mod = []
            for pname in _splitname:
                pname
                _match = [_pk for _pk in self.peak_collection.options if any(pname == _p for _p in _pk.split('_'))]
                if _match:
                    if len(_match) == 1:
                        if _match[0] in self.substrate_peak and not self.add_substrate:
                            raise ValueError(f'Substrate peak included in { self._model_name}, however add_substrate is {self.add_substrate}')
                        _mod.append(_match[0])
            self.mod_lst = _mod
            self.eval_mod_str()
            if self.add_substrate:
                self.add_substrate_to_model()
                
        
        if hasattr(self, 'model'):
            self.model_prefix_name = '+'.join([i.prefix[:-1] for i in self.model.components])
        
    def eval_mod_str(self):
        if self.mod_lst:
            _mod_str = ' + '.join([f'self.peak_collection.{peak}.model' for peak in self.mod_lst])
            try:
                _model = eval(_mod_str)
                self.model = _model
            except Exception as e:
                print(f'Exception in eval of model string {_mod_str}:\n{e}')
                raise e
                
    def __repr__(self):
        _txt = f'{self.model_prefix_name}: '
        if hasattr(self,'model'):
            _txt += repr(self.model)    
        else:
            _txt += 'empty model'
        return _txt
    
    
class InitializeModels():
    
    peak_collection = Peak_Collection()
    _standard_1st_order = {'2peaks' : 'G+D',
                            '3peaks' : 'G+D+D3',
                            '4peaks' : 'G+D+D3+D4',
                            '5peaks' : 'G+D+D2+D3+D4',
                            '6peaks' : 'G+D+D2+D3+D4+D5'}
    
    _standard_2nd_order = {'2nd_4peaks' : 'D4D4+D1D1+GD1+D2D2'}

                   
    def __init__(self, standard_models = True):
        self.construct_standard_models()    
        self.normalization_model = self.peak_collection.normalization
        
    def construct_standard_models(self):
        
        _models = {}
        
        _models_1st = {f'1st_{key}+Si' : BaseModel(peak_collection = self.peak_collection, model_name=value) 
                       for key,value in self._standard_1st_order.items()}
        _models.update(_models_1st)
        _models_1st_no_substrate = {f'1st_{key}' : BaseModel(peak_collection = self.peak_collection, model_name=value, add_substrate=False, substrate_peak='')
                                    for key,value in self._standard_1st_order.items()}
        _models.update(_models_1st_no_substrate)
        self.first_order = {**_models_1st, **_models_1st_no_substrate}
        
        
        _models_2nd = {key : BaseModel(peak_collection = self.peak_collection, model_name=value, add_substrate=False, substrate_peak='')
                       for key,value in self._standard_2nd_order.items()}
        _models.update(_models_2nd)
        self.second_order = _models_2nd
        
        self.all_models = _models

    
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


def _remove():
    
    def _old_Fit_model_options():
        peak_options = ['4peaks','5peaks','6peaks']
        _extra = ['Si_substrate']
    # ====== MODEL CHOICE ======= #
    
    def old_test_for_Si_substrate(model):
        '''make test fit for only slice 900-1000
        if amplitude of Si_substrate peak > 1 than set true to include in model otherwise false'''
    
    class old_ModelChoices:
        def __init__(self,choice: str):
            self.model = ModelChoices.Choice2Model(choice)
        
        
        def PeakOptions():
            return ['Lorentzian','Gaussian','Voigt']
        def ModelOptions():
    #        ['2peaks','3peaks']
            return ['4peaks', '5peaks', '6peaks']
        
        def ModelOptions_2ndOrder():
            return ['2ndOrder_4peaks']
        
        def Choice2Model(fitmodel,add_Si_substrate = True):
            if '2ndOrder_4peaks' in fitmodel:
                Model =  D4D4_peak().mod + D1D1_peak().mod + GD1_peak().mod + D2D2_peak().mod
            
            else:
                if '2peaks' in fitmodel:
                    if 'normalization' in fitmodel:
                        if any(i in fitmodel for i in ModelChoices.PeakOptions()):
                            normpeak = [i for i in ModelChoices.PeakOptions() if i in fitmodel][0]
            #            normpeak = 'Voigt' #'Lorentzian'
                        Model = G_peak(normalization=True,  PeakType = normpeak).mod + D_peak(normalization=True, PeakType = normpeak).mod
                    else:
                        Model = G_peak().mod + D_peak().mod
                    
                elif '3peaks' in fitmodel:
                    Model = G_peak().mod + D_peak().mod + D3_peak().mod
                
                elif '4peaks' in fitmodel:
                    Model = G_peak().mod + D_peak().mod + D3_peak().mod + D4_peak().mod
                    Model.param_hints['G_center']['min'] = 1565
                    Model.param_hints['D_center']['max'] = 1365
                    Model.param_hints['D3_center']['max'] = 1520
                    Model.param_hints['D4_center']['max'] = 1240
                    Model.param_hints['D4_center']['value'] = 1215
                    
                elif '5peaks' in fitmodel:
                    Model = G_peak().mod + D_peak().mod + D2_peak().mod + D3_peak().mod + D4_peak().mod
                
                elif '6peaks' in fitmodel:
                    Model = G_peak().mod + D_peak().mod + D2_peak().mod + D3_peak().mod + D4_peak().mod + D5_peak().mod
                    
                else:
                    print(f'Model not in options {ModelChoices.ModelOptions()}, {fitmodel}')
                    Model = G_peak().mod + D_peak().mod
                if add_Si_substrate:
                    Model = Model + Si_substrate_peak().mod
            return Model
    #    def Choice2Model_2ndOrder(fitmodel):
    #            Model = G_peak().mod + D_peak().mod + D3_peak().mod
    
    def _start_fitting(fitting_specs):
        spec_1st = [i for i in fitting_specs if i.windowname=='1st_order'][0]
    #    fit_spec_1st,info_spec_1st = mean_spec[sIDmean_col], mean_info
        try:
            results_1st = FittingLoop_1stOrder(spec_1st)
        except:
            results_1st = FittingLoop_1stOrder(spec_1st)
    #    elif wn == '2nd_order':
    #    fit_spec_2nd, info_spec_2nd  = mean_spec[sIDmean_col], mean_info
        spec_2nd = [i for i in fitting_specs if i.windowname=='2nd_order'][0]
    #    fit_spec_2nd,mean_info_2nd
        results_2nd = FittingLoop_2ndOrder(spec_2nd)
        results_1st,results_2nd = ModelChoices.Combined_ratioparams(results_1st,results_2nd)
        # TODO plotting each peak model with 2nd order
        return results_1st,results_2nd 
    #    model_options = ModelChoices.ModelOptions()
    #    for peak in model_options:
    #        try:
    #            fitting_export(results_1st.get(peak),results_2nd )
    #        except:
    #            print('Fitting export failed')
            
    def _FittingLoop_1stOrder(spec_1st, model_options = ModelChoices.ModelOptions()):
        fit_spec_1st,info_spec_1st = spec_1st.mean_spec[spec_1st.sIDmean_col], spec_1st.mean_info
        '''fitting_1storder with different peak models...'''
        x, y = fit_spec_1st.index.values, fit_spec_1st.values
        Result_peak_nt = namedtuple('FitResults', ['FitComponents','FitParameters','extrainfo','peak_model', 'raw_data_col', 'FitReport'])
        results = {}
        
        for peak_model in model_options:
            try:
                FittingComps, FittingParams, FitReport = Fit_1stOrder_Carbon(x,y,peak_model = peak_model, 
                                                                  export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col)
                Result_peak = Result_peak_nt(FittingComps, FittingParams, info_spec_1st, peak_model, spec_1st.sIDmean_col, FitReport)
                results.update({peak_model : Result_peak})
    #   TODO fitting multi
    #   results = run_fitting_multi(x,y,export_info = info_spec_1st, PreFit = False, raw_data_col = spec_1st.sIDmean_col, model_options = model_option)
            except Exception as e:
                results.update({peak_model : Result_peak, 'Error_Exception' : e})
    #        results.append(Result_peak)
        return results
       
    def _Fit_1stOrder_Carbon(x,y,peak_model = '6peaks', export_info = pd.DataFrame(), PreFit = False, raw_data_col = 'raw_data'):
    #        x,y,FileName,blcor = self.w1,self.i1_blcor,self.FileName,self.blcor
    #       x,y,FileName = PosInts_Bg['RamanShift'].values,PosInts_Bg[SampleBgmean_col].values,'%s_mean'%sID
        GammaVary = False
        Model = ModelChoices(peak_model).model
        params = Model.make_params()
    
        if PreFit:
            pre_fit = Model.fit(y,params,x=x, method='differential-evolution') # 'leastsq'
    #        pre_fit.plot(show_init=True)
    #        print(pre_fit.fit_report())
            out = Model.fit(y,pre_fit.params,x=x,method='leastsq') # 'leastsq'
    #        out.plot(show_init=True)
    #        print(out.fit_report())
        else:
           out = Model.fit(y,params,x=x,method='leastsq') # 'leastsq'
    #       out.plot(show_init=True)
    #       print(out.fit_report())
    #    print(f'pre={pre_fit.redchi:.3G}, out={out.redchi:.3G}, pre_out = {out_pre.redchi:.3G}')
        fit_params_od = {'SampleID' : export_info.SampleID.unique()[0]}
        fit_params_od.update(out.params.valuesdict())
        fit_attr_export_lst = ('chisqr','redchi','bic','aic', 'method','message','success','nfev')
        fit_atrrs = OrderedDict(zip(fit_attr_export_lst,[getattr(out,i) for i in fit_attr_export_lst]))
        fit_params_od.update(fit_atrrs)
        fit_params_od.update(ModelChoices.RatioParams(fit_params_od,Model))
        fit_params_od.update({'run_date_YmdH' : datetime.datetime.now().strftime(format='%Y-%m-%d %H:00')})
    #        pd.datetime.now().strftime(format='%Y-%m-%d %H:00')})
        # TODO add ratios 
        FittingParams = pd.DataFrame(fit_params_od,index=[peak_model])
    #    [(i,a.value) for i,a in fit_params.items()]
        fit_comps = out.eval_components(x=x)
        fit_comps_out = OrderedDict({'RamanShift' : x})
        fit_comps_out.update(fit_comps)
        fit_comps_out.update({f'Model_{peak_model}' : out.best_fit, 'residuals' : out.residual, raw_data_col : y})
        FittingComps = pd.DataFrame(fit_comps_out)
        '''make export stuff'''
        return FittingComps, FittingParams, out.fit_report(show_correl=False)
    
    
    
    def _old_funcs():
        #TODO remove        
        def PeakTypeChooser(PeakType,prefix_set):
            if 'Lorentzian' in PeakType:
                model = LorentzianModel(prefix=prefix_set)
            elif 'Gaussian' in PeakType:
                model = GaussianModel(prefix=prefix_set)
            elif 'Voigt' in PeakType:
                model = VoigtModel(prefix=prefix_set)
            return model
        
        def make_model_hints(mod,hints):
           for pname,pars in hints.items():
               mod.set_param_hint(pname,**pars)
           return mod
    
    
    
    
    def _old_second_order_peaks():
        #TODO remove
        # ====== SECOND ORDER PEAKS ======= #
        class D4D4_peak():
            '''2nd order D4 peak '''
        #        D2D2_mod = VoigtModel(prefix='D2D2_')
            def __init__(self, PeakType = 'Lorentzian', prefix='D4D4_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D4D4_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 2435,'min' : 2400, 'max' : 2550},
                            'sigma' : {'value' : 30,'min' : 1, 'max' : 200},
                            'amplitude' : {'value' : 2,'min' : 1E-03, 'max' : 100}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        #                    'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}}
                return settings
        
        class D1D1_peak():
            '''2nd order D(1) peak, aka 2D
            2450 cm􀀀1 band, which has been attributed recently to a D + D” 
            band by Couzi et al. [61], the D + D’ (in literature, the wrong D + G label is often found [62]), the
            2D’ bands and the 2D + G band.
            1627 and 2742 cm􀀀1 bands as the D’ and 2D
            '''
            def __init__(self, PeakType = 'Lorentzian', prefix='D1D1_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D1D1_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 2650,'min' : 2600, 'max' : 2750},
                            'sigma' : {'value' : 60,'min' : 1, 'max' : 200},
                            'amplitude' : {'value' : 14,'min' : 1E-03, 'max' : 100}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                    
                return settings
        
        class GD1_peak():
            '''2nd order G+D(1) peak '''
        #        D2D2_mod = VoigtModel(prefix='D2D2_')
            def __init__(self, PeakType = 'Lorentzian', prefix='GD1_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = GD1_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 2900,'min' : 2800, 'max' : 2950},
                            'sigma' : {'value' : 50,'min' : 1, 'max' : 200},
                            'amplitude' : {'value' : 10,'min' : 1E-03, 'max' : 100}}
                if GammaVary:
                    setttings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
        
        class D2D2_peak():
            '''2nd order D2 peak, aka 2D2'''
        #        D2D2_mod = VoigtModel(prefix='D2D2_')
            def __init__(self, PeakType = 'Lorentzian', prefix='D2D2_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D2D2_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 3250,'min' : 3000, 'max' : 3400},
                            'sigma' : {'value' : 60,'min' : 20, 'max' : 200},
                            'amplitude' : {'value' : 1,'min' : 1E-03, 'max' : 100}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
        # ====== SECOND ORDER PEAKS ======= #
        
        
        # === Adding extra peak at 2450 and run FIT again ===
        # 2D graphite 
        def _FittingLoop_2ndOrder(spec_2nd, model_options = ModelChoices.ModelOptions_2ndOrder()):           
            '''fitting_2nd_order with different peak models...'''
            fit_spec_2nd,mean_info_2nd = spec_2nd.mean_spec[spec_2nd.sIDmean_col], spec_2nd.mean_info
        #    Fit_VoigtModel_PyrCarbon_2ndOrder(x,y,peak_model = peak_model, export_info = mean_info, PreFit = False)
            x, y = fit_spec_2nd.index.values, fit_spec_2nd.values
            Result_peak_nt = namedtuple('FitResults', ['FitComponents','FitParameters','extrainfo','peak_model', 'raw_data_col', 'FitReport'])
            results_2nd = {}
            for peak_model in model_options:
                FittingComps, FittingParams, FitReport = Fit_2ndOrder_Carbon(x,y,peak_model = peak_model, 
                                                                  export_info = mean_info_2nd, PreFit = False, raw_data_col = spec_2nd.sIDmean_col)
                Result_peak = Result_peak_nt(FittingComps, FittingParams, mean_info_2nd, peak_model, spec_2nd.sIDmean_col, FitReport)
        #        results.append(peak_model : Result_peak)
                results_2nd.update({peak_model : Result_peak})
            return results_2nd    
            
        def _Fit_2ndOrder_Carbon(x,y,peak_model = '2ndOrder_4peaks', export_info = pd.DataFrame(), PreFit = False, raw_data_col = 'raw_data'):
        #        x,y,FileName,blcor = self.w1,self.i1_blcor,self.FileName,self.blcor
        #       x,y,FileName = PosInts_Bg['RamanShift'].values,PosInts_Bg[SampleBgmean_col].values,'%s_mean'%sID
            GammaVary = False
            Model =  ModelChoices(peak_model).model
            params = Model.make_params()
        
            if PreFit:
                pre_fit = Model.fit(y,params,x=x, method='differential-evolution') # 'leastsq'
        #        pre_fit.plot(show_init=True)
        #        print(pre_fit.fit_report())
                out = Model.fit(y,pre_fit.params,x=x,method='leastsq') # 'leastsq'
        #        out.plot(show_init=True)
        #        print(out.fit_report())
            else:
               out = Model.fit(y,params,x=x,method='leastsq') # 'leastsq'
        #       out.plot(show_init=True)
        #       print(out.fit_report())
        #    print(f'pre={pre_fit.redchi:.3G}, out={out.redchi:.3G}, pre_out = {out_pre.redchi:.3G}')
            fit_params_od = {'SampleID' : export_info.SampleID.unique()[0]}
            fit_params_od.update(out.params.valuesdict())
            fit_attr_export_lst = ('chisqr','redchi','bic','aic', 'method','message','success','nfev')
            fit_atrrs = OrderedDict(zip(fit_attr_export_lst,[getattr(out,i) for i in fit_attr_export_lst]))
            fit_params_od.update(fit_atrrs)
            fit_params_od.update(ModelChoices.RatioParams_2ndOrder(fit_params_od,Model)) # 2nd order
            fit_params_od.update({'run_date_YmdH' : datetime.datetime.now().strftime(format='%Y-%m-%d %H:00')})
        #    fit_params_od.update({'run_date_YmdH' : pd.datetime.now().strftime(format='%Y-%m-%d %H:00')})
            # TODO add ratios 
            FittingParams = pd.DataFrame(fit_params_od,index=[peak_model])
        #    [(i,a.value) for i,a in fit_params.items()]
            fit_comps = out.eval_components(x=x)
            fit_comps_out = OrderedDict({'RamanShift' : x})
            fit_comps_out.update(fit_comps)
            fit_comps_out.update({f'Model_{peak_model}' : out.best_fit, 'residuals' : out.residual, raw_data_col : y})
            FittingComps = pd.DataFrame(fit_comps_out)
            '''make export stuff'''
            return FittingComps, FittingParams, out.fit_report(show_correl=False)
        
    
    
    # ====== FIRST ORDER PEAKS ======= #
    
    def _old_first_order_peaks():
        '''
        Notes:
        Für D1: 1340-1350
        Für D3: 1495-1515
        Für G: 1580-1590
        D5 und D2 weiß ich nicht
        '''
        
        class G_peak():
            '''Graphite belongs to the P63/mmc (D46h) space group. If considering only a graphene plane, at 
            the Ã point of the Brillouin zone, there are six normal modes that possess only one mode (doubly
            degenerate in plane) with a E2g representation, which is Raman active
            G ; Ideal graphitic lattice (E2g-symmetry)
            G peak center stable over different laser wavelengths. Influenced by potential, HSO4 adsorption (or ionization of G- and G+),
            magnetic fields, pressure
            '''
            def __init__(self, PeakType = 'Lorentzian', prefix='G_', GammaVary = False, normalization = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = G_peak.param_hints(GammaVary, normalization)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary, normalization ):
                settings = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
                            'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                            'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
                if normalization:
                     settings = {'center' : {'value' : 1581, 'min' : 1500, 'max' : 1600},
                            'sigma' : {'value' : 40, 'min' : 1E-05},
                            'amplitude' : {'value' : 8E4, 'min' : 1E2}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
            
        
        class D_peak():
            ''' D or D1 ; Disordered graphitic lattice (graphene layer edges,A1gsymmetry)
            A defective graphite presents other bands that can be as intense as the G band at D=1350 and D'=1615 cm-1
            These bands are activated by defects due to the breaking of the crystal symmetry that relax the Raman selection rules'''
        
            def __init__(self, PeakType = 'Lorentzian', prefix='D_', GammaVary = False,normalization = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D_peak.param_hints(GammaVary, normalization)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary,normalization):
                settings = {'center' : {'value' : 1350,'min' : 1330, 'max' : 1380},
                            'sigma' : {'value' : 35,'min' : 1, 'max' : 150},
                            'amplitude' : {'value' : 120,'min' : 1E-05, 'max' : 500}}
                if normalization:
                     settings = {'center' : {'value' : 1350,'min' : 1300, 'max' : 1400},
                            'sigma' : {'value' : 90, 'min' : 1E-05},
                            'amplitude' : {'value' : 10E5, 'min' : 1E2}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        
                return settings
        
        
        class D2_peak():
            '''D2 or D' ; Right next to the G peak, sometimes not obvious as G peak split.
            Disordered graphitic lattice (surface graphene layers,E2g-symmetry)
            j.molstruc.2010.12.065'''
        
            def __init__(self, PeakType = 'Lorentzian', prefix='D2_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D2_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 1606,'min' : 1592, 'max' : 1635},
                            'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                            'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
        
        class D3_peak():
            ''' D3 or D'' or A or Am ; Between the D and G peak, sometimes too broad.
            For amorphous carbon (Gaussian[26]or Lorentzian[3,18,27]line shape)'''
        
            def __init__(self, PeakType = 'Lorentzian', prefix='D3_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D3_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 1480, 'min' : 1450, 'max' : 1505},
                            'sigma' : {'value' : 25,'min' : 1, 'max' : 150},
                            'amplitude' : {'value' : 25,'min' : 1E-02, 'max' : 500}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
        
        class D4_peak():
            ''' D4 or I ; Below D band, a shoulder sometimes split with D5 band.
            Disordered graphitic lattice (A1gsymmetry)[10],polyenes[3,27], ionic impurities
            D4 peak at 1212 cm−1
            Jurkiewicz, K., Pawlyta, M., Zygadło, D. et al. J Mater Sci (2018) 53: 3509. https://doi.org/10.1007/s10853-017-1753-7
            Für D4: 1185-1210, but depends on if there is D5 or not'''
        
            def __init__(self, PeakType = 'Lorentzian', prefix='D4_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D4_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 1230,'min' : 1180, 'max' : 1290},
                            'sigma' : {'value' : 40,'min' : 1, 'max' : 150},
                            'amplitude' : {'value' : 20,'min' : 1E-02, 'max' : 200}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
           
        class D5_peak():
            '''D5 peak at 1110 cm−1. At lowest should of D peak, below D4.
            Ref: Jurkiewicz, K., Pawlyta, M., Zygadło, D. et al. J Mater Sci (2018) 53: 3509. https://doi.org/10.1007/s10853-017-1753-7
            '''
            def __init__(self, PeakType = 'Lorentzian', prefix='D5_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = D5_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 1150,'min' : 1100, 'max' : 1200},
                            'sigma' : {'value' : 40,'min' : 1, 'max' : 150},
                            'amplitude' : {'value' : 20,'min' : 1E-02, 'max' : 200}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
        
        class Si_substrate_peak():
            '''===== Extra peak at ca. 960 cm-1 presumably from Si substrate 2nd order === not from Nafion...
            => Either cut the Spectra 1000-2000
            => Place an extra Gaussian peak at 960 in the fit
            '''
            def __init__(self, PeakType = 'Gaussian', prefix='Si_substrate_', GammaVary = False):
                self.model = PeakTypeChooser(PeakType,prefix)
                self.param_hints = Si_substrate_peak.param_hints(GammaVary)
                self.mod = make_model_hints(self.model,self.param_hints)
                
            def param_hints(GammaVary):
                settings = {'center' : {'value' : 960,'min' : 900, 'max' : 980},
                            'sigma' : {'value' : 10,'min' : 0, 'max' : 150},
                            'amplitude' : {'value' : 10,'min' : 0, 'max' : 200}}
                if GammaVary:
                    settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
                return settings
        
        
        # ====== FIRST ORDER PEAKS ======= #
    
    
