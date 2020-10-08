#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:51:17 2020

@author: zmg
"""

'''

Für D1: 1340-1350
Für D3: 1495-1515
Für G: 1580-1590
D5 und D2 weiß ich nicht
'''
from collections import OrderedDict,namedtuple

import datetime
import pandas as pd
import lmfit
from lmfit.models import VoigtModel,LorentzianModel, GaussianModel



def Fit_model_options():
    
    '4peaks'
    '5peaks'
    '6peaks'
    '6peaks, Si_substrate'
    
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

def test_for_Si_substrate(model):
    '''make test fit for only slice 900-1000
    if amplitude of Si_substrate peak > 1 than set true to include in model otherwise false'''

class ModelChoices:
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
    def RatioParams(fit_params_od,Model):
        peaks = [i.prefix for i in Model.components]
        rt = [('I','_height'), ('A','_amplitude')]
        RatioParams = {}
        if 'G_' and 'D_' in peaks:
            for a,t in rt:
                RatioParams.update({f'{a}D/{a}G' : fit_params_od['D'+t]/fit_params_od['G'+t]})
                RatioParams.update({f'La_{a}G' : 4.4*RatioParams.get(f'{a}D/{a}G')**-1})
#                , 'ID/IG' : fit_params_od['D_height']/fit_params_od['G_height']}
            if 'D2_' in peaks:
                for a,t in rt:
                    RatioParams.update({f'{a}D/({a}G+{a}D2)' : fit_params_od['D'+t]/(fit_params_od['G'+t]+fit_params_od['D2'+t])})
                    RatioParams.update({f'La_{a}G+D2' : 4.4*RatioParams.get(f'{a}D/({a}G+{a}D2)')**-1})
#                    : fit_params_od['D'+t]/(fit_params_od['G'+t]+fit_params_od['D2'+t])})
                if 'D3_' in peaks:
                    for a,t in rt:
                        RatioParams.update({f'{a}D3/({a}G+{a}D2' : fit_params_od['D3'+t]/(fit_params_od['G'+t]+fit_params_od['D2'+t])})
            if 'D3_' in peaks:
                for a,t in rt:
                    RatioParams.update({f'{a}D3/{a}G' : fit_params_od['D3'+t]/fit_params_od['G'+t]})
            if 'D4_' in peaks:
                RatioParams.update({f'{a}D4/{a}G' : fit_params_od['D4'+t]/fit_params_od['G'+t]})
        return RatioParams

    def RatioParams_2ndOrder(fit_params_od,Model):
        peaks = [i.prefix for i in Model.components]
        rt = [('I','_height'), ('A','_amplitude')]
        RatioParams = {}
        if 'D1D1_' and 'GD1_' in peaks:
            for a,t in rt:
                RatioParams.update({f'{a}D1D1/{a}GD1' : fit_params_od['D1D1'+t]/fit_params_od['GD1'+t]})
        return RatioParams
#                RatioParams.update({f'La_{a}G' : 4.4*RatioParams.get(f'{a}D/{a}G')**-1})
#                , 'ID/IG' : fit_params_od['D_height']/fit_params_od['G_height']}
#            if 'D2_' in peaks:
#                for a,t in rt:
#                    RatioParams.update({f'{a}D/({a}G+{a}D2)' : fit_params_od['D'+t]/(fit_params_od['G'+t]+fit_params_od['D2'+t])})
#                    RatioParams.update({f'La_{a}G+D2' : 4.4*RatioParams.get(f'{a}D/({a}G+{a}D2)')**-1})
##                    : fit_params_od['D'+t]/(fit_params_od['G'+t]+fit_params_od['D2'+t])})
#     ratioI2D_I2G = I_D1D1/I_D2D2
#    A2D_A2G = outPars['D1D1_amplitude']/outPars['D2D2_amplitude']
#    RatioPars = {'I2D/I2G' : ratioI2D_I2G,'A2D/A2G' : A2D_A2G,
    def Combined_ratioparams(results_1st,results_2nd):
        rt = [('I','_height'), ('A','_amplitude')]
        for key2,val2 in results_2nd.items():
            fitpars_2nd = val2.FitParameters
            
            for k1,v1 in results_1st.items():
                fitpars_1st = v1.FitParameters    
                
                for a,t in rt:
                    fitpars_1st['D1D1'+t] = fitpars_2nd['D1D1'+t].values
                    fitpars_1st = fitpars_1st.assign(**{f'Leq_{a}' : 8.8*fitpars_1st['D1D1'+t]/fitpars_1st['D'+t]})
                v1 = v1._replace(**{'FitParameters' : fitpars_1st})
                results_1st[k1] = v1
        return results_1st,results_2nd
        
#    try:
#            FitPars['L_eq_I'] = 8.8*FitPars_2nd['I_D1D1']/FitPars['I_D']
#        except:
#            FitPars['L_eq_I'] = 0
#        try:
#            FitPars['L_eq'] = 8.8*FitPars_2nd['D1D1_amplitude']/FitPars['D_amplitude']
#        except:
#            FitPars['L_eq'] = 0
#%%
#                    {'ID/(IG+ID2)' : fit_params_od['D_height']/fit_params_od['G_height']}
#        ratioID_IG,ratioID3_IG = I_D/I_G,I_D3/I_G
#        AD_AG, AD2_AG = outPars['D_amplitude']/outPars['G_amplitude'],outPars['D2_amplitude']/outPars['G_amplitude']
#        AD3_AG, AD4_AG = outPars['D3_amplitude']/outPars['G_amplitude'],outPars['D4_amplitude']/outPars['G_amplitude']
    
#        RatioPars = {'ID/IG' : ratioID_IG,'L_a_I' : 4.4*ratioID_IG, 'L_a' : 4.4*(AD_AG**-1), 'AD/AG' : AD_AG, 'AD2/AG' : AD2_AG,
#                 'AD3/AG' : AD3_AG, 'AD4/AG' : AD4_AG,'ID3/IG' : ratioID3_IG,
#                 'ChiSqr': out.chisqr,'RedChiSqr' : out.redchi,'ResMean' : out.residual.mean(),
#                  'I_D' : I_D,  'I_D3' : I_D3,'I_D4' : I_D4,'I_G' : I_G, 'FitModel' : str(mod)}
#    D_mod = D_peak().mod
#    D2_mod = D2_peak().model_hints
#    test_Si_substrate
#    mod = G_peak().mod+D_peak().mod
#    if FitModel_1st == '4peaks':
#        mod = G_mod + D_mod + D3_mod + D4_mod 
#    if '5peaks' in FitModel_1st:
#        mod = G_mod + D_mod + D2_mod + D3_mod + D4_mod 
#        if 'Si_substrate' in FitModel_1st:
#            mod += Si_substrate_mod
#    if '6peaks' in FitModel_1st:
#        mod = G_mod + D_mod + D2_mod + D3_mod + D4_mod + D5_mod
#        if 'Si_substrate' in FitModel_1st:
#            mod += Si_substrate_mod

def NormalizeFit(norm_cleaner,plotprint = False):
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

def start_fitting(fitting_specs):
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
        
def FittingLoop_1stOrder(spec_1st, model_options = ModelChoices.ModelOptions()):
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
   
def Fit_1stOrder_Carbon(x,y,peak_model = '6peaks', export_info = pd.DataFrame(), PreFit = False, raw_data_col = 'raw_data'):
#        x,y,FileName,blcor = self.w1,self.i1_blcor,self.FileName,self.blcor
#       x,y,FileName = PosInts_Bg['RamanShift'].values,PosInts_Bg[SampleBgmean_col].values,'%s_mean'%sID
#%%
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
#    FitData = pd.DataFrame({'RamanShift' :x,'G_peak' : comps['G_'],'D_peak' : comps['D_'],'D4_peak' : comps['D4_'],
#                  'D3_peak' : comps['D3_'], 'I_data' : out.data,'I_model4Voigt' : out.best_fit, 'residuals' : out.residual})
##    pd.DataFrame([(i,a.value) for i,a in fit_params.items()])
    # TODO test if parameters hit bounds
#        print('%s\n'%out.message,out.fit_report(min_correl=0.90))
#    [i.prefix for i in Model.components]
#    FWHM = {'D_fwhm' : out.params['D_fwhm'].value, 'D4_fwhm' : out.params['D4_fwhm'].value,'D3_fwhm' : out.params['D3_fwhm'].value,'G_fwhm' : out.params['G_fwhm'].value,'SampleID' : FileName.split('_')[0]}
#    HEIGHT = {'D_height' : out.params['D_height'].value, 'D4_height' : out.params['D4_height'].value,'D3_height' : out.params['D3_height'].value,'G_height' : out.params['G_height'].value}
#    outPars = out.best_values
#    outPars.update(FWHM)
#    outPars.update(HEIGHT)
#    I_D = FitData.loc[ np.isclose(outPars['D_center'],FitData['RamanShift'],rtol=0.003),'D_peak'].mean()
#    I_D3 = FitData.loc[ np.isclose(outPars['D3_center'],FitData['RamanShift'],rtol=0.003),'D3_peak'].mean()
#    I_D4 = FitData.loc[ np.isclose(outPars['D4_center'],FitData['RamanShift'],rtol=0.003),'D4_peak'].mean()
#    I_G = FitData.loc[ np.isclose(outPars['G_center'],FitData['RamanShift'],rtol=0.003),'G_peak'].mean()
    
    #%%
#    return out,comps,FitPars,FitData,pre_fit
#if normalization:
#             settings = {'center' : {'value' : 1350,'min' : 1300, 'max' : 1400},
#                    'sigma' : {'value' : 90, 'min' : 1E-05},
#                    'amplitude' : {'value' : 10E5, 'min' : 1E2}}

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

# === Adding extra peak at 2450 and run FIT again ===
# 2D graphite 
def FittingLoop_2ndOrder(spec_2nd, model_options = ModelChoices.ModelOptions_2ndOrder()):           
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
    
def Fit_2ndOrder_Carbon(x,y,peak_model = '2ndOrder_4peaks', export_info = pd.DataFrame(), PreFit = False, raw_data_col = 'raw_data'):
#        x,y,FileName,blcor = self.w1,self.i1_blcor,self.FileName,self.blcor
#       x,y,FileName = PosInts_Bg['RamanShift'].values,PosInts_Bg[SampleBgmean_col].values,'%s_mean'%sID
#%%
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

#def Fit_VoigtModel_PyrCarbon_2ndOrder(self,SampleID):
#    # TESTING ====
##        a = SpectrumAnalyzer(w,i,'%s_mean'%sID,2100,3500)
##        x,y,FileName,blcor,SampleID = a.w1,a.i1_blcor,a.FileName,a.blcor,'TE3'
#    x,y,FileName,blcor = self.w1,self.i1_blcor,self.FileName,self.blcor
##        N2_bg = SpectrumAnalyzer(self.Rash,self.Int,self.Filename,2100,3000).subtract_bg()
##        x,y,FileName,blcor = N2_bg.w1,N2_bg.i1_blcor,self.FileName,N2_bg.blcor
##        self.w,self.i_blcor,self.blcor,self.w1,self.i1_blcor
##        D1D1_mod = VoigtModel(prefix='D1D1')
## === TWO Fitting loops ====
##        mod = D1D1mod + D2D2_mod 
##        init =  mod.eval(pars, x=x)
##        out = mod.fit(y,pars,x=x,method='leastsq')
##        comps = out.eval_components(x=x)
#    Model = G_peak().mod + D_peak().mod + D2_peak().mod + D3_peak().mod + D4_peak().mod + D5_peak().mod
#    mod_3peaks = D1D1_mod + D2D2_mod + D4D4_mod + GD1_mod
#    init_3peaks =  mod_3peaks.eval(pars, x=x)
#    out_3peaks = mod_3peaks.fit(y,pars,x=x,method='leastsq')
#    comps_3peaks = out_3peaks.eval_components(x=x)
##       ====
##        print('3peaks: %s, 2 peaks : %s'%(out_3peaks.redchi,out.redchi))
##        if out_3peaks.redchi < out.redchi:
##        else: outFinal,compsFinal,initFinal = out,comps,init
##  --- No checking which Fit is best, just go for the 3 peaks model --- #
#    outFinal,compsFinal,initFinal = out_3peaks,comps_3peaks,init_3peaks
##       ----
##        All parameters for Output ====
##        print('%s\n'%outFinal.message,outFinal.fit_report(min_correl=0.90))
#    FWHM = {'D1D1_fwhm' : outFinal.params['D1D1_fwhm'].value,'D2D2_fwhm' : outFinal.params['D2D2_fwhm'].value,
#            'D4D4_fwhm' : outFinal.params['D4D4_fwhm'].value, 'GD1_fwhm' : outFinal.params['GD1_fwhm'].value,
#            'SampleID' : SampleID}
#    outPars = outFinal.best_values
#    outPars.update(FWHM)
#    FitData = pd.DataFrame({'RamanShift' :x,'D2D2_peak' : compsFinal['D2D2_'],'D1D1_peak' : compsFinal['D1D1_'],
#                            'D4D4_peak' : compsFinal['D4D4_'],'GD1_peak' : compsFinal['GD1_'],
#                            'I_data' : outFinal.data,'I_model4Voigt' : outFinal.best_fit})
#    I_D1D1 = FitData.loc[ np.isclose(outPars['D1D1_center'],FitData['RamanShift'],rtol=0.003),'D1D1_peak'].mean()
#    I_D2D2 = FitData.loc[ np.isclose(outPars['D2D2_center'],FitData['RamanShift'],rtol=0.003),'D2D2_peak'].mean()
#    I_D4D4 = FitData.loc[ np.isclose(outPars['D4D4_center'],FitData['RamanShift'],rtol=0.003),'D4D4_peak'].mean()
#    I_GD1 = FitData.loc[ np.isclose(outPars['GD1_center'],FitData['RamanShift'],rtol=0.003),'GD1_peak'].mean()
#   
#    outPars.update(RatioPars)
##    plot_components,plot_Annotation = True,True
#    FitPars = pd.DataFrame(outPars,index=[FileName])
#    return outFinal,compsFinal,FitPars,FitData,initFinal