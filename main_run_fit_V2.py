#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:49:20 2020

@author: zmg
"""
import sys
from collections import namedtuple
from operator import itemgetter
from pathlib import Path


import numpy as np
import hashlib


import pandas as pd

## for in spec analyzer
import matplotlib.pyplot as plt
from scipy import signal
from scipy.stats import linregress


##

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))
    from FileHelper.FindFolders import FindExpFolder
    from FileHelper.FindSampleID import SampleIDstr,GetSampleID
    from FileHelper.PostChar import SampleSelection, Characterization_TypeSetting
    from RAMANpy.indexer import OrganizeRamanFiles
    from RAMANpy.fit_models import NormalizeFit, start_fitting
#    from RAMANpy.fit_models import FittingLoop_1stOrder, FittingLoop_2ndOrder
    from RAMANpy.plotting import raw_data_export, fit_spectrum_plot
    
else:
    sys.path.append(str(Path(__file__).parent.parent))
    from FileHelper.FindFolders import FindExpFolder
    from FileHelper.FindSampleID import SampleIDstr,GetSampleID
    from FileHelper.PostChar import SampleSelection, Characterization_TypeSetting
#from ..FileHelper import FindExpFolder,SampleIDstr,FindSampleID

#from indexer import *
from functools import reduce
from itertools import chain
from operator import add
def namedtuplemerge(*args):
    cls = namedtuple('_'.join(arg.__class__.__name__ for arg in args), reduce(add, (arg._fields for arg in args)))
    return cls(*chain(*args))

#%%

class RamanLoop():
    '''documentaion .......
    '''
    
    def __init__():
        pass
    def test_positions(sGrp_grp,nm, grp_cols = ['FileStem','SamplePos','FilePath']):
#        grp_cols = ['FileStem','SamplePos','FileCreationDate']
        if sGrp_grp.FileStem.nunique() != sGrp_grp.SamplePos.nunique():
            print(sGrp_grp[grp_cols])
            print(f'Unique files and positions not matching for {nm}')
            return sGrp_grp.groupby(grp_cols),grp_cols
        else:
            return sGrp_grp.groupby(grp_cols),grp_cols
        
    def add_make_destdirs(sGr, sGrp_grp):
        DestDir = sGrp_grp.DestDir.unique()[0]
        DestGrpDir = DestDir.joinpath(sGr)
        DestFitPlots, DestFitComps = DestGrpDir.joinpath('Fitting_Plots'), DestGrpDir.joinpath('Fitting_Components')
#        DestFitPlots.mkdir(parents=True,exist_ok=True)
        DestFitComps.mkdir(parents=True,exist_ok=True)
        DestRawData = DestGrpDir.joinpath('Raw_Data')
        DestRawData.mkdir(parents=True,exist_ok=True)
        export_info = {'DestGrpDir' : DestGrpDir,'DestFittingPlots' : DestFitPlots,'DestFittingComps' : DestFitComps,'DestRaw' : DestRawData}
        return export_info 
    
    def test_spectra_lengths(sample_spectra):
        lengths = [i.spectrum_length for i in sample_spectra]
        set_lengths = set(lengths)
        if len(set_lengths) == 1:
#            print(f'Spectra all same length {set_lengths}')
            return sample_spectra
        else:
            length_counts = [(i, lengths.count(i)) for i in set_lengths]
            best_guess_length = max(length_counts,key=itemgetter(1))[0]
            print(f'Spectra not same length {length_counts} took {best_guess_length}')
            return [i for i in sample_spectra if i.spectrum_length == best_guess_length]
    
    def GrpNames():
        sGrp_cols = ('SampleGroup', 'SampleID', 'FileCreationDate')
        sPos_cols = ('FileStem','SamplePos','FilePath')
        spectrum_cols = ('ramanshift', 'intensity_raw', 'intensity')
        spectrum_info_cols = ('spectrum_length',)
        export_info_cols  = ('DestGrpDir', 'DestFittingPlots', 'DestFittingComps', 'DestRaw' )
        info_cols = sGrp_cols+ sPos_cols + spectrum_cols + spectrum_info_cols + export_info_cols
        names = {'sGrp_cols' : sGrp_cols,'sPos_cols' : sPos_cols, 'spectrum_cols' : spectrum_cols,
                 'spectrum_info_cols' : spectrum_info_cols,'export_info_cols' : export_info_cols, 'all' : info_cols}
        Names = namedtuple('GrpNames', names.keys())
#        output_ary = np.array(output)   # this is your matrix 
#        output_vec = output_ary.ravel() # this is your 1d-array
        return Names(**names)
    
    def SpecrumTemplate(name = 'spectrum_info'):
        return namedtuple(name, RamanLoop.GrpNames().all)
                    
    def run_index(RamanIndex):
        GrpNames = RamanLoop.GrpNames()
#        info_cols = sGrp_cols+ sPos_cols + spectrum_cols + spectrum_info_cols
        Spectrum = RamanLoop.SpecrumTemplate()
        all_spectra = {}
        all_index = []
        FitParams1, FitParams2 = [], []
        for grpnm, sGrp_grp in RamanIndex.groupby(GrpNames.sGrp_cols[0]):
            all_index = []
            for nm, sID_grp in RamanIndex.groupby(list(GrpNames.sGrp_cols[1:])):
                sGr, (sID, sDate) = grpnm, nm
                
                sGr_out = dict(zip(GrpNames.sGrp_cols,(grpnm,)+nm))
                export_info_out = RamanLoop.add_make_destdirs(sGr,sID_grp)
                sample_pos_grp,sPos_cols = RamanLoop.test_positions(sID_grp,nm,list(GrpNames.sPos_cols))
                
                sample_spectra = []
                for meannm, meangrp in sample_pos_grp:
#                    print(meannm)
                    
                    ramanshift, intensity_raw= np.array([]),np.array([])
                    i = 0
                    while not ramanshift.any():
                        try:
                            ramanshift, intensity_raw = np.loadtxt(meannm[-1], usecols=(0, 1), unpack=True, skiprows=i)
                            print(meannm, len(ramanshift),len(intensity_raw))
                        except ValueError:
                            i += 1
                            
                            
                        
                    intensity = SpectrumCleaner.filtered(intensity_raw)
                    sPos_out = dict(zip(GrpNames.sPos_cols,meannm))
                    spectrum_out = dict(zip(GrpNames.spectrum_cols+GrpNames.spectrum_info_cols, (ramanshift, intensity_raw, intensity, len(ramanshift))))
                    sample_spectrum_position_info = Spectrum(**{**sGr_out, **export_info_out, **sPos_out, **spectrum_out})
                    
    #                dict(zip(GrpNames.all,nm+meannm+(ramanshift, intensity_raw, intensity, len(ramanshift)))
    #                sample_spectrum_position_info = Spectrum(**dict(zip(GrpNames.all,nm+meannm+(ramanshift, intensity_raw, intensity, len(ramanshift)))))
                    
                    sample_spectra.append(sample_spectrum_position_info)
                sample_spectra = RamanLoop.test_spectra_lengths(sample_spectra)
                speclst = PrepareMean_Fit.subtract_baseline(sample_spectra)
                fitting_specs = PrepareMean_Fit.calc_mean_from_spclst(speclst) # TODO return mean of spectra 
                raw_data_export(fitting_specs) # TODO RAW data export and plotting
                results_1st,results_2nd = start_fitting(fitting_specs)
                pars1,pars2 = export_fitting_plotting_peak(results_1st,results_2nd )
                FitParams1.append(pars1), FitParams2.append(pars2)
            index = export_FitParams_Grp(FitParams1, FitParams2, export_info_out, grpnm,sID)
            all_index.append(index)
            pars_index = pd.DataFrame(*all_index,columns=list(GrpNames.sGrp_cols[0:2] +('PeakModel','DestPars')))
            pars_index.to_excel( export_info_out.get('DestGrpDir').joinpath(f'{sGr}_index.xlsx'))
        
        

def export_FitParams_Grp(FitParams1, FitParams2, export_info_out, grpnm, sID):
    pars1, pars2 = pd.concat(FitParams1,sort=False), pd.concat(FitParams2,sort=False)
    DestGrpDir = export_info_out.get('DestGrpDir')
    indexes = []
    for pknm, pkgrp in pars1.groupby(pars1.index):
        peak_destpath = DestGrpDir.joinpath(f'{grpnm}_FitParameters_Model_{pknm}')
        pkgrp.dropna(axis=1).to_excel(peak_destpath.with_suffix('.xlsx'), index=False)
        indexes.append((grpnm, sID, pknm, peak_destpath))
#    peak_destpath_extra = res_peak_spec.extrainfo.DestFittingComps.unique()[0].joinpath(f'Extra_{res_peak_spec.peak_model}_{sID}')
    for pknm2, pkgrp2 in pars2.groupby(pars2.index):
        peak_destpath = DestGrpDir.joinpath(f'{grpnm}_FitParameters_Model_{pknm2}')
        pkgrp2.dropna(axis=1).to_excel(peak_destpath.with_suffix('.xlsx'), index=False)
        indexes.append((grpnm, sID, pknm, peak_destpath))
    return indexes
       
# res_peak_spec.extrainfo.to_excel(peak_destpath_extra.with_suffix('.xlsx'), index=False)
#        
#    pars1, pars2 = [], []
#    for peak2,res2_peak_spec  in results_2nd.items():
#        export_xls_from_spec(res2_peak_spec)
#        pars2.append(res2_peak_spec.FitParameters)
#        for peak1,res1_peak_spec in results_1st.items():
#            export_xls_from_spec(res2_peak_spec)     
#            fit_spectrum_plot(peak1,res1_peak_spec,res2_peak_spec, plot_Annotation = True, plot_Residuals = True)
#            pars1.append(res1_peak_spec.FitParameters)
#    return pd.concat(pars1,sort=False), pd.concat(pars2,sort=False)
#           
            
#            and start fitting
            # Exporting and Plotting

def export_fitting_plotting_peak(results_1st, results_2nd):
    pars1, pars2 = [], []
    for peak2,res2_peak_spec  in results_2nd.items():
        export_xls_from_spec(res2_peak_spec)
        pars2.append(res2_peak_spec.FitParameters)
        for peak1,res1_peak_spec in results_1st.items():
            export_xls_from_spec(res1_peak_spec) 
            try:
                fit_spectrum_plot(peak1,res1_peak_spec,res2_peak_spec, plot_Annotation = True, plot_Residuals = True)
            except Exception as e:
                print(f'Error fit_spectrum_plot:{peak1}, {res1_peak_spec.raw_data_col}.\n {e}'  )
            pars1.append(res1_peak_spec.FitParameters)
    return pd.concat(pars1,sort=False), pd.concat(pars2,sort=False)
            

def export_xls_from_spec(res_peak_spec):
    sID = res_peak_spec.extrainfo.SampleID.unique()[0]
    peak_destpath = res_peak_spec.extrainfo.DestFittingComps.unique()[0].joinpath(f'Model_{res_peak_spec.peak_model}_{sID}')
    peak_destpath_extra = res_peak_spec.extrainfo.DestFittingComps.unique()[0].joinpath(f'Extra_{res_peak_spec.peak_model}_{sID}')
    res_peak_spec.FitComponents.to_excel(peak_destpath.with_suffix('.xlsx'), index=False)
    res_peak_spec.extrainfo.to_excel(peak_destpath_extra.with_suffix('.xlsx'), index=False)
#    Model_peak_col = res_peak_spec.peak_model Model_data_col = f'Model_{Model_peak_col_2nd}' 
#    destdir = res_peak_spec.extrainfo.DestFittingComps.unique()[0]    
    
#    res1_peak_spec.FitComponents.to_excel(peak_destdir.with_suffix('.xlsx'),index=False)
#    res_peak_spec.extrainfo

class PrepareMean_Fit():
    '''
    Operations so far: read-raw-spectrum > savgol_filter > 
    normalization on (filtered,despiked,baseline-corrected) G peak
    for i in peak range:
        do baseline substraction
        take normalizion in normal window
    slice, filter, despike, slice, subtract baseline, '''
    
    def __init__(self):
        pass
      
    def subtract_baseline(sample_spectra):
        speclst = []
        for spec_raw in sample_spectra:
    #        spectrum = namedtuple('Spectrum', 'ramanshift intensity')
            FirstOrder_spec = SpectrumCleaner(SpectraInfo.spec_slice(spec_raw,'1st_order'))
    #        SpectrumCleaner(SpectraInfo.spec_slice(norm_spec,windowname)).spec
            norm_spec = SpectrumCleaner.normalization(FirstOrder_spec,spec_raw)
            # TODO appending each region and make columns of position and mean for fitting and plotting....
    #        cleaner = SpectrumCleaner(SpecWindow)
            for windowname,(low,high) in SpectraInfo.SpectrumWindows().items():
                window_spec = SpectraInfo.spec_slice(norm_spec,windowname)
                cleaned_window_spec = SpectrumCleaner(window_spec)
    #            cleaned_wind_spec.plot()
                speclst.append(PrepareMean_Fit.norm_spec_unpack_appender(cleaned_window_spec.cleaned_spec))    
        return speclst
     
    def norm_spec_unpack_appender(norm_spec):
        spec_length = norm_spec.spectrum_length
        array_test = [(n,i) for n,i in zip(norm_spec._fields,norm_spec) if 'array' in str(type(i))]
        array_cols = [i[0] for i in array_test] # arrays = [i[1] for i in array_test]
        spec_info = dict([(i,getattr(norm_spec,i)) for i in norm_spec._fields if i not in array_cols])
        
        
    #    spec_array_sliced = dict([(i[0],i[1][ind]) for i in array_test])
    
#    norm_spec._asdict()
        return pd.DataFrame( norm_spec._asdict()).set_index(list(spec_info.keys()))
    
    def calc_mean_from_spclst(speclst):
        spectras = pd.concat(speclst)
        mean_spclst = namedtuple('MeanSpectras' , 'windowname sID_rawcols sIDmean_col mean_info mean_spec')
        results_spclst = []
        for wn,wgrp in spectras.groupby('windowname'):
    #        pd.DataFrame(wgrp.index.names, wgrp.index.to_flat_index())
#            wgrp.plot(x='ramanshift',y='intensity',title=wn)
            mean_wn = pd.DataFrame()
            mean_info = wgrp.index.to_frame().drop_duplicates()
            mean_info = mean_info.set_index('FileStem')
            sID = mean_info.SampleID.unique()[0]
            sIDmean_col = f'int_{sID}_mean'
            
            for idx,idxgrp in wgrp.groupby(level='FileStem'):
    #            idxgrp.plot(x='ramanshift',y='intensity_raw',title=f'{wn} {idx}')
                pos_spectrum = idxgrp[['ramanshift','intensity']].rename(columns={'intensity' : f'intensity_{idx}'}).set_index('ramanshift')
                if mean_wn.empty:
                    mean_wn = pos_spectrum
                else:
    #                mean_wm.update(pos_spectrum)
#                    print(wn,idx)
                    mean_wn = pd.merge(mean_wn,pos_spectrum,on='ramanshift',how='left')
            sID_rawcols = [i for i in mean_wn.columns if 'intensity' in i]
            mean_spec = mean_wn.assign(**{sIDmean_col : mean_wn[sID_rawcols].mean(axis=1)})
            diff_mean_info = []
            for infFS,infFSgrp in mean_info.groupby(level='FileStem'):
                diff_mean_spec = mean_spec[sIDmean_col] - mean_spec[f'intensity_{infFS}']
                diff_mean_info.append(np.abs(diff_mean_spec).sum())
            mean_info = mean_info.assign(**{f'diff_from_{sIDmean_col}' : diff_mean_info})
            
            prep_fit_spec = mean_spclst(wn,sID_rawcols, sIDmean_col,mean_info, mean_spec)
            results_spclst.append(prep_fit_spec)
        return results_spclst
#           continue_with_mean_fitting_exporting(wn,fit_spec, mean_info )
            # TODO continue here wiht means
#            return wn,mean_spec,mean_info
#    
#    def continue_with_mean_fitting_exporting(wn,fit_spec,mean_info):
#        '''Standard export raw files peak models...'''
#        # TODO export raw files standard
#        if wn == '1st_order':
#            FittingLoop(wn, fit_spec,mean_info)
#            
#            '''fitting_1storder with different peak models...'''
#        elif wn == '2nd_order':
#            '''fitting_1storder with different peak models...'''
    
class SpectrumCleaner():
    
    def __init__(self,spec):
#        self.raw_intensity = spec.intensity
        self.spec = spec
#        self.int_savgol = SpectrumCleaner.filtered(spec.intensity)
        self.Despike_raw = Despike(spec.intensity_raw)
        self.despiked_raw_intensity = self.Despike_raw.despiked_int
        self.despiked_raw_df = self.Despike_raw.df
        self.blcorr_desp_intensity_raw,self.blc_dsp_int_raw_lin = SpectrumCleaner.subtract_baseline(self,  self.despiked_raw_intensity)
        
        self.Despike_filter = Despike(spec.intensity)
        self.despiked_intensity = self.Despike_filter.despiked_int
#        breakpoint()
        self.despiked_df = self.Despike_filter.df
        self.blcorr_desp_intensity,self.blc_dsp_int_linear = SpectrumCleaner.subtract_baseline(self,  self.despiked_intensity)
        
#TODO self.df = SpectrumCleaner.pack_to_dataframe(self)
        self.cleaned_spec = SpectrumCleaner.cleaned_out_spec(self)
        
    def filtered(intensity):
#        fltrd_spec = self.raw_spec
        int_savgol_fltr = signal.savgol_filter(intensity, 13, 3, mode='nearest')
#        fltrd_spec._replace(intensity=int_savgol_fltr)
        return int_savgol_fltr
    
    def pack_to_df_names():
         return ('ramanshift', 'intensity_raw', 'intensity','int_raw_despike',
                 'int_filter_despike', 'int_filter_despike_blcorr', 'int_raw_despike_blcorr')
         
    def pack_to_dataframe(self):
        cols = [self.spec.ramanshift, self.spec.intensity_raw,  self.spec.intensity, 
                self.despiked_raw_intensity, self.despiked_intensity, self.blcorr_desp_intensity, self.blcorr_desp_intensity_raw] 
        names = SpectrumCleaner.pack_to_df_names()
        return pd.DataFrame(dict(zip(names,cols)))
    
    def cleaned_out_spec(self):
        cleanSpec_template = self.spec
        cleanSpec = cleanSpec_template._replace(intensity = self.blcorr_desp_intensity, intensity_raw = self.blcorr_desp_intensity_raw)
        return cleanSpec
    
    def plot(self):
        self.df.plot(x='ramanshift',y=[i for i in list(SpectrumCleaner.pack_to_df_names()[1:]) if 'blcorr' in i])     
        
    def subtract_baseline(self, i_fltrd_dspkd_input):
        rs = self.spec.ramanshift
        windowname = self.spec.windowname
#        self.spec = SpectraInfo.spec_slice(spec_raw,'1st_order')
#        i_fltrd_dspkd_input = Despike(self.spec.intensity).despiked_int
#        rs_min, rs_max = rs.min(), rs.max()
        
        if windowname == 'full':
            indx = SpectraInfo.ramanshift_slice_indx(rs, '1st_order')
            i_fltrd_dspkd_fit = i_fltrd_dspkd_input[indx]
        else:
            i_fltrd_dspkd_fit = i_fltrd_dspkd_input
        
        if windowname in ['1st_order','full', 'full_1st_2nd']:
            bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:20]),np.mean(i_fltrd_dspkd_fit[-20::])])
        elif windowname == '2nd_order':
            bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:5]),np.mean(i_fltrd_dspkd_fit[-5::])])
        else:
            bl_linear = linregress(rs[[0,-1]],[np.mean(i_fltrd_dspkd_fit[0:10]),np.mean(i_fltrd_dspkd_fit[-10::])])
        i_blcor = i_fltrd_dspkd_input - (bl_linear[0]*rs+bl_linear[1])
#        blcor = pd.DataFrame({'Raman-shift' : w, 'I_bl_corrected' :i_blcor, 'I_raw_data' : i})
        return i_blcor,bl_linear
    
    def normalization(FirstOrder_spec,output_spec,method='simple'):
        if 'simple' in method:
            indx_norm = SpectraInfo.ramanshift_slice_indx(FirstOrder_spec.spec.ramanshift,'normalization')
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(spec,'normalization'))
            normalization_intensity  = FirstOrder_spec.blcorr_desp_intensity[indx_norm].max()
            
        elif 'fit' in method:
#            prep_norm_spec = SpectrumCleaner(SpectraInfo.spec_slice(FirstOrder_spec,'1st_order'))
            normalization = NormalizeFit(FirstOrder_spec,plotprint = False)
            normalization_intensity = normalization['IG']
            
        norm_dict = {'norm_factor' : 1/normalization_intensity, 'norm_method' : method}
        int_fields = [i for i in output_spec._fields if 'intensity' in i]
        extra_info_flds = [i for i in output_spec._fields if i not in int_fields]
        [norm_dict.update({i : getattr(output_spec,i)}) for i in extra_info_flds]
        [norm_dict.update({i : getattr(output_spec, i)/normalization_intensity}) for i in int_fields]
        norm_info = namedtuple('norm_info','norm_factor norm_method')
        NormSpec = namedtuple('spectrum_normalized', RamanLoop.SpecrumTemplate()._fields + norm_info._fields)(**norm_dict)
        return NormSpec
#        namedtuple('Spectrum_clean',self.spec._fields)
##        spec_length = spec.spectrum_length
#        array_test = [(n,i) for n,i in zip(self.spec._fields,self.spec) if 'array' in str(type(i))]
#        array_cols = [i[0] for i in array_test] # arrays = [i[1] for i in array_test]
#        spec_info = dict([(i,getattr(self.spec,i)) for i in self.spec._fields if i not in array_cols])
#        spec_arrays = {'ramanshift' : self.spec.ramanshift, 
#                       'intensity' : self.blcorr_desp_intensity, 'intensity_raw' : self.blcorr_desp_intensity_raw}
#        cleanSpec = cleanSpec_template({**spec_info,**spec_arrays})
#        return cleanSpec 
#        NormSpec(**[extra_info + intensity_normalized])
#        SpecWindow = SpectraInfo.spec_slice(spec,'1st_order')
#        norm_cleaner = SpectrumCleaner(SpecWindow)
#        norm_cleaner.df
#        fitting_norm
#%%           
def test_window_plot(xy_lst):
#    xy_lst = [(spec_window_rs,spec_window_int)]
    fig,ax =plt.subplots()
    for xy in xy_lst:
        x,y = xy
        ax.plot(x,y)
#        y_fltr = signal.savgol_filter(y, 5, 3, mode='nearest')
#        ax.plot(x,y_fltr,c='g')
    plt.show()
    plt.close()
#class spectrum_filter():
#    __slots__ = ()
#    @property
#    def filtered(self):
#        return signal.savgol_filter(self.intensity, 13, 3, mode='nearest')
#    @property
#    def hypot(self):
#        return (self.x ** 2 + self.y ** 2) ** 0.5
#    def __str__(self):
#        return 'Point: x=%6.3f  y=%6.3f  hypot=%6.3f' % (self.x, self.y, self.hypot)
#            if 'full' in windowname:
##                spec_clean = namedtuple('Spectrum_cleaned', spec._fields + SpectraInfo.clean_spec_cols())
#                SpecWindow = SpectraInfo.spec_slice(spec,windowname)
#                cleaner = SpectrumCleaner(SpecWindow)
#                cleaner.plot()
##                windowname,(low,high)
##                ind = (spec.ramanshift >= low) & (spec.ramanshift <= high)
##                spec_window_rs,spec_window_int = spec.ramanshift[ind],spec.intensity[ind]
##                cleaner.Despike_filter.plot_Z()
#                cleaner.pack_to_dataframe()
#            cleaner.df.plot()
            # TODO ALL PLOT ARE SAME
#            test_window_plot([(spec_window_rs,spec_window_int),(spec_window_rs,Despike(spec_window_int).spectrum)])        
class SpectraInfo():
    '''takes namedtuple with spectra'''
    
    def __init__(self):
        self.window = SpectraInfo.SpectrumWindows()
    
    def SpectrumWindows():
        windows = {'full' : (200,3600), 'full_1st_2nd' : (800,3500), 'low' : (150,850), '1st_order' : (900,2000),
                   'mid' : (1850,2150), '2nd_order' : (2000,3380), 'normalization' : (1500,1675)}
        return windows

    def ramanshift_slice_indx(ramanshift, windowname):
        low,high = SpectraInfo().window[windowname]
        ind = (ramanshift >= low) & (ramanshift <= high)
        return ind

    def spec_slice(spec,windowname):
        ind = SpectraInfo.ramanshift_slice_indx(spec.ramanshift, windowname)
        
        SpecSlice_template = namedtuple('SpectrumSliced',spec._fields+('windowname',))
        spec_length = spec.spectrum_length
        array_test = [(n,i) for n,i in zip(spec._fields,spec) if 'array' in str(type(i)) and len(i) == spec_length]
        array_cols = [i[0] for i in array_test] # arrays = [i[1] for i in array_test]
        spec_info = dict([(i,getattr(spec,i)) for i in spec._fields if i not in array_cols])
        spec_array_sliced = dict([(i[0],i[1][ind]) for i in array_test])
        SpecSlice = SpecSlice_template(**{**spec_info,**spec_array_sliced, **{'windowname' : windowname}})
        return SpecSlice
        
    
    def clean_spec_cols():
        return ('Zt', 'Zt_threshold','int_despike','int_filter_despike')
    
    def check_input_return_intensity(test):
        type_test = str(type(test))
        if '__main__' in type_test:
            if 'intensity' in test._fields:
                int_used = test.intensity
        elif 'numpy.ndarray' in type_test:
            int_used = test
        elif 'dict' in type_test:
            int_used = test.get([i for i in test.keys() if 'intensity' in i][0])
#             = test
        else:
            print(f'Despike input error {type_test}')
            int_used = test
        return int_used
         
#class Spectrum(spec):
#    """adding functionality to a named tuple"""
#    def __init__():
#        self.intensity = spec.intensity
#    __slots__ = ()
#    @property
#    def savgol_filter(self):
#        return signal.savgol_filter(self.intensity, 13, 3, mode='nearest')
#        def __str__(self):
#            return 'Point: x=%6.3f  y=%6.3f  hypot=%6.3f' % (self.x, self.y, self.hypot)       
    
class Despike():
    '''Let Y1;...;Ynrepresent the values of a single Raman spectrum recorded at equally spaced wavenumbers.
    From this series, form the detrended differenced seriesr Yt ...:This simple
    ata processing step has the effect of annihilating linear and slow movingcurve linear trends, however,
    sharp localised spikes will be preserved.Denote the median and the median absolute deviation of 
    D.A. Whitaker, K. Hayes. Chemometrics and Intelligent Laboratory Systems 179 (2018) 82–84
    https://doi.org/10.1016/j.chemolab.2018.06.009'''
    def __init__(self,input_intensity):
        self.intensity = SpectraInfo.check_input_return_intensity(input_intensity)
        self.Zt = Despike.calc_Z(self.intensity)
        self.Zt_filter = Despike.Z_filter(self.Zt)
        self.despiked_int = Despike.fixer(self.intensity, self.Zt_filter)
        self.df = Despike.pack_to_df(self)
        self.dict = Despike.pack_to_dict(self)
#        self. = Despike.fixer(intensity,Despike.Z_filter(intensity))
    
    def pack_to_df(self):
        cols =  [self.intensity, self.Zt, self.Zt_filter, self.despiked_int] 
        names = ['intensity','Zt', 'Zt_threshold','int_despike']
        return pd.DataFrame(dict(zip(names,cols)))
    
    def pack_to_dict(self):
        cols =  [self.intensity, self.Zt, self.Zt_filter, self.despiked_int] 
        names = ['intensity','Zt', 'Zt_threshold','int_despike']
        return dict(zip(names,cols))
    
    def plot_Z(self):
        self.df.plot(y=['Zt', 'Zt_threshold'],alpha=0.5)
   # TODO still finish...
    def calc_Z(intensity): 
#        y = intensity[Ystr]
        dYt = np.append(np.diff(intensity),0)
        #    dYt = intensity.diff()
        dYt_Median = np.median(dYt)
        #    M = dYt.median()
        #    dYt_M =  dYt-M
        dYt_MAD = np.median(abs(dYt - dYt_Median))
        #    MAD = np.mad(dYt)
        Z_t = (0.6745*(dYt-dYt_Median)) / dYt_MAD
        #    intensity = blcor.assign(**{'abs_Z_t': Z_t.abs()})
        return Z_t
    
    def Z_filter(Z_t, Z_threshold = 6):
        Z_t_filtered = Z_t
        Z_t_filtered[np.abs(Z_t) > Z_threshold] = np.nan
        Z_t_filtered[0] = Z_t_filtered[-1] = np.nan
        return Z_t_filtered
#        Z_threshold = 3.5
#        Z_t_filtered = [Z_t
#        Z_t_filtered[Z_filter_indx] = np.nan
#        y_out,n = intensity,len(intensity)
    
    def fixer(intensity,Z_t_filtered,ma=10):
        n = len(intensity)
        i_despiked = intensity
        spikes = np.where(np.isnan(Z_t_filtered))
        for i in list(spikes[0]):
            w = np.arange(max(1,i-ma),min(n,i+ma))
            w = w[~np.isnan(Z_t_filtered[w])]
            i_despiked[i] = np.mean(intensity[w]) 
        return i_despiked
#        if blcor.query('abs_Z_t > @Zmin').empty:
#            print('No spikes in window')
#            i_blcor = blcor[Ystr].values
#        else:
#            blcor.query('abs_Z_t > @Zmin')
#            #        blcor.rolling(on='I_bl-corrected',window=10).mean().plot(x='Raman-shift',y='I_bl-corrected')
#            blcor = blcor.assign(**{'I_spike_corr': blcor[Ystr]})
#            blcor.loc[blcor['abs_Z_t'] > Zmin, 'I_spike_corr'] = np.nan
#            blcor['I_spike_corr'].interpolate(method = 'nearest',inplace=True)
#            #        blcor = blcor.assign(**{'I_spike_corr': blcor['I_bl_corrected'].interpolate(method = 'nearest')})
#        #        blcor.plot(x='Raman-shift', y=['I_bl_corrected', 'I_spike_corr'])
#        i_blcor = blcor['I_spike_corr'].values
#        #            print('!Spikes are removed!')
#        #        print(len(w),len(i),len(i_blcor))
#        return blcor,i_blcor    
#%%
#def __init__(self):
#    self.low_range = [190,800]
#    self.first_order = [800,2000]
#    self.mid_range = [1800,2150]
#    self.second_order = [2100,3300]
#    self.normalization = [1575,1620]
#    orgRFs,freqMin = 800,freqMax = 2000,plot_Components = False,plot_Annotation = True,plot_Residuals = False,
#                   GammaVary = False,RAMAN_bgCorr_Plot = False,norm_window=[1575,1620],
#                   freqr_2nd = [2100,3300], norm_window_2nd = [2550,2700], 
#                   freqr_low = [190,800],   norm_window_low = [190,800],
#                   freqr_mid = [1800,2150],   norm_window_mid = [1800,2150],
#                   SampleGroupDef = '', FitModPeaks = '6peaks,Si_substrate' ):
#    def make_mean_sample_grp(sample_spectra):
#        pass
##                DestSmplDir.mkdir(parents=True,exist_ok=True)
#        PosSample,PosRS0,PosInts0,PosInts0_Bg,PosInts0_Bg_2nd,FS1,PosInts0_Bg_low, PosInts0_Bg_mid={},{},{},{},{},{},{},{}
#### ==== Prepare Average Spectrum of positions. === ####
#        print('Taking mean of {2} files for Sample: {0} of group {1} and fitting.'.format(sID,sGrp,len(grp)))
#        for (FileStem,SamplePos,FileCreationDate),grp in sample_pos_grp:
#            print(FileStem)
#            grp
#            fp,Pos = row.Filepath, row.SamplePos
#            FileName = os.path.splitext(os.path.basename(fp))[0]
##            DestDir.mkdir(parents=True,exist_ok=True) 
#            DestGrpDir.mkdir(parents=True,exist_ok=True)
##                    FileHelper.FileOperations.make_path(DestDir),FileHelper.FileOperations.make_path(DestGrpDir)
#            try:
#                w, i = np.loadtxt(fp, usecols=(0, 1), unpack=True)
#                
##                        pd.read_csv(fp,sep='\t',names=['Frequency','Intenity_{0}'.format(Pos)]).set_index('Frequency')
##                i_Bg = SpectrumAnalyzer(w,i,FileName).S()[0]
#                try:
#                    SpecInit = SpectrumAnalyzer(w,i,FileName)
#                    i1_Bg, w1_Bg, i_bg, w_bg  = SpecInit.i1_blcor, SpecInit.w1,SpecInit.i_blcor,SpecInit.w
#                    SpecInit_2nd = SpectrumAnalyzer(w,i,FileName,freqr_2nd[0],freqr_2nd[1])
##                            SpecInit_2nd = SpectrumAnalyzer(w,i,FileName,freqr_2nd[0],freqr_2nd[1])
#                    i1_Bg_2nd, w1_Bg_2nd, i_bg_2nd, w_bg_2nd  = SpecInit_2nd.i1_blcor, SpecInit_2nd.w1,SpecInit_2nd.i_blcor,SpecInit_2nd.w
#                    
#                    SpecInit_low = SpectrumAnalyzer(w,i,FileName,freqr_low[0],freqr_low[1],RAMAN_bgCorr_Plot=True)
#                    i1_Bg_low, w1_Bg_low, i_bg_low, w_bg_low  = SpecInit_low.i1_blcor, SpecInit_low.w1,SpecInit_low.i_blcor,SpecInit_low.w
#                    
#                    SpecInit_mid = SpectrumAnalyzer(w,i,FileName,freqr_mid[0],freqr_mid[1],RAMAN_bgCorr_Plot=True)
#                    i1_Bg_mid, w1_Bg_mid, i_bg_mid, w_bg_mid  = SpecInit_mid.i1_blcor, SpecInit_mid.w1,SpecInit_mid.i_blcor,SpecInit_mid.w
#                except:
#                    print('Spectrum initialization problem, CRITICAL!')
##                        print(len(w),len(i),len(i1_Bg),len(w1_Bg))
##                        DataOut = {'RamanShift' : w,'Int' : i}
#                PosRS0.update({'RamanShift_%s'%Pos : w})
#                PosInts0.update({'%s'%FileName : i })
#                ind1,ind = (w1_Bg > norm_window[0]) & (w1_Bg < norm_window[1]), (w > norm_window[0]) & (w < norm_window[1])
##                        ind1_2nd,ind_2nd = (w1_Bg_2nd > norm_window_2nd[0]) & (w1_Bg_2nd < norm_window_2nd[1]), (w > norm_window_2nd[0]) & (w < norm_window_2nd[1])
##                         < norm_window[1]
#                norm= 1/i1_Bg[ind1].max()
##                       normFS,normi = 1/i_bg[ind].max(),1/i[ind].max()
##                        norm_2nd,normFS_2nd,normi_2nd = 1/i1_Bg_2nd[ind1_2nd].max(),1/i_bg_2nd[ind_2nd].max(),1/i[ind_2nd].max()
#                FS1.update({'raw_{0}_{1}'.format(FileName,grNm) : i,'raw_norm_{0}_{1}'.format(FileName,grNm) : i*norm, 'despiked_{0}_{1}'.format(FileName,grNm)  : i_bg, 'despiked_norm_{0}_{1}'.format(FileName,grNm)  : i_bg*norm})
#                
#                PosInts0_Bg.update({'%s_Bg'%FileName : i1_Bg*norm })
#                PosInts0_Bg_2nd.update({'%s_Bg'%FileName : i1_Bg_2nd*norm})
#                PosInts0_Bg_low.update({'%s_Bg'%FileName : i1_Bg_low*norm})
#                PosInts0_Bg_mid.update({'%s_Bg'%FileName : i1_Bg_mid*norm})
#                
#            except Exception as e:
#                print('DATA Problem %s, %s:'%(UgrNm,grNm),e)
#                continue 
#            PosRS,PosInts,PosInts_Bg,FS= pd.DataFrame(PosRS0),pd.DataFrame(PosInts0),pd.DataFrame(PosInts0_Bg),pd.DataFrame(FS1)
#            PosInts_Bg_2nd = pd.DataFrame.from_dict(PosInts0_Bg_2nd,orient='index').transpose().iloc[0:len(w1_Bg_2nd)]
#            PosInts_Bg_low = pd.DataFrame.from_dict(PosInts0_Bg_low,orient='index').transpose().iloc[0:len(w1_Bg_low)]
#            PosInts_Bg_mid = pd.DataFrame.from_dict(PosInts0_Bg_mid,orient='index').transpose().iloc[0:len(w1_Bg_mid)]
#            
#
#        
#        RAMAN_dir = FileHelper.FindExpFolder('RAMAN').DestDir
##        OrganizeRAMANFiles().ovv()[0]
#        DBpath = FileHelper.FindExpFolder('RAMAN').DestDir / 'RAMAN_DB.hdf5' 
#        if len(FitModPeaks.split(',')) > 1:
#            plot_extra = FitModPeaks.split(',')[0]
#        else:
#            plot_extra =  ''
#        print('Fitting the Raman Spectra that are found in folder: "%s"\nUsing Frequency window for fitting %s - %s cm^-1' %(RAMAN_dir,freqMin,freqMax))
#        print('Plot Basline Correction: %s\nPlot Fitting Components: %s\nPlot Peak Annotations: %s\nPlot Residuals: %s\nVary Gamma in fit: %s'
#              %(RAMAN_bgCorr_Plot,plot_Components,plot_Annotation,plot_Residuals,GammaVary))
#        AllResult = pd.DataFrame([])
#        for UgrNm,Ugrp in orgRFs.groupby(['SampleGroup']):
#            GrOut,GrOut2,GrOutFS,RResult = pd.DataFrame([]),pd.DataFrame([]),pd.DataFrame([]),pd.DataFrame([])
#            sGrp = UgrNm
#            for grNm,grp in Ugrp.groupby(['SampleID']):
##                print(sGrp+'/',grNm)
#                DestDir = grp.DestDir.unique()[0]
#                sID = grNm
#                DestGrpDir,DestSmplDir = DestDir.joinpath(sGrp),DestDir.joinpath(sGrp,sID)
#                
#                DestPlotDir, DestFitCompsDir, DestExtraPlots= DestGrpDir.joinpath('Plots_{0}'.format(plot_extra)), DestGrpDir.joinpath('FitComps_{0}'.format(plot_extra)), DestGrpDir.joinpath('RawDataPlots')
##                DestSmplDir.mkdir(parents=True,exist_ok=True)
#                DestPlotDir.mkdir(parents=True,exist_ok=True)
#                DestFitCompsDir.mkdir(parents=True,exist_ok=True)
#                DestExtraPlots.mkdir(parents=True,exist_ok=True)
#                PosSample,PosRS0,PosInts0,PosInts0_Bg,PosInts0_Bg_2nd,FS1,PosInts0_Bg_low, PosInts0_Bg_mid={},{},{},{},{},{},{},{}
#        ### ==== Prepare Average Spectrum of positions. === ####
#                print('Taking mean of {2} files for Sample: {0} of group {1} and fitting.'.format(sID,sGrp,len(grp)))
#        
#                    
#    @staticmethod
#    def plot_RAMAN(orgRFs,freqMin = 800,freqMax = 2000,plot_Components = False,plot_Annotation = True,plot_Residuals = False,
#                   GammaVary = False,RAMAN_bgCorr_Plot = False,norm_window=[1575,1620],
#                   freqr_2nd = [2100,3300], norm_window_2nd = [2550,2700], 
#                   freqr_low = [190,800],   norm_window_low = [190,800],
#                   freqr_mid = [1800,2150],   norm_window_mid = [1800,2150],
#                   SampleGroupDef = '', FitModPeaks = '6peaks,Si_substrate' ):
## TESTING below       
## freqMin,freqMax,plot_Components,plot_Annotation,plot_Residuals,GammaVary,RAMAN_bgCorr_Plot,PostProcess,norm_window,norm_window_2nd,SampleGroupDef,freqr_2nd =  800, 2000, True, True,True, False, False,True,[1575,1620], [2550,2700],'M',[2100,3300] 
##norm_window_low, freqr_low = [200,800], [200,800]
##freqr_mid, norm_window_mid = [1800,2150], [1800,2150]
##SampleGroupDef, FitModPeaks = '','6peaks,Si_substrate'
##%%
##        orgRFs = orgRFs.query('SampleID == "MK238"')
#        RAMAN_dir = FileHelper.FindExpFolder('RAMAN').DestDir
##        OrganizeRAMANFiles().ovv()[0]
#        DBpath = FileHelper.FindExpFolder('RAMAN').DestDir / 'RAMAN_DB.hdf5' 
#        if len(FitModPeaks.split(',')) > 1:
#            plot_extra = FitModPeaks.split(',')[0]
#        else:
#            plot_extra =  ''
#        print('Fitting the Raman Spectra that are found in folder: "%s"\nUsing Frequency window for fitting %s - %s cm^-1' %(RAMAN_dir,freqMin,freqMax))
#        print('Plot Basline Correction: %s\nPlot Fitting Components: %s\nPlot Peak Annotations: %s\nPlot Residuals: %s\nVary Gamma in fit: %s'
#              %(RAMAN_bgCorr_Plot,plot_Components,plot_Annotation,plot_Residuals,GammaVary))
#        AllResult = pd.DataFrame([])
#        for UgrNm,Ugrp in orgRFs.groupby(['SampleGroup']):
#            GrOut,GrOut2,GrOutFS,RResult = pd.DataFrame([]),pd.DataFrame([]),pd.DataFrame([]),pd.DataFrame([])
#            sGrp = UgrNm
#            for grNm,grp in Ugrp.groupby(['SampleID']):
##                print(sGrp+'/',grNm)
#                DestDir = grp.DestDir.unique()[0]
#                sID = grNm
#                DestGrpDir,DestSmplDir = DestDir.joinpath(sGrp),DestDir.joinpath(sGrp,sID)
#                
#                DestPlotDir, DestFitCompsDir, DestExtraPlots= DestGrpDir.joinpath('Plots_{0}'.format(plot_extra)), DestGrpDir.joinpath('FitComps_{0}'.format(plot_extra)), DestGrpDir.joinpath('RawDataPlots')
##                DestSmplDir.mkdir(parents=True,exist_ok=True)
#                DestPlotDir.mkdir(parents=True,exist_ok=True)
#                DestFitCompsDir.mkdir(parents=True,exist_ok=True)
#                DestExtraPlots.mkdir(parents=True,exist_ok=True)
#                PosSample,PosRS0,PosInts0,PosInts0_Bg,PosInts0_Bg_2nd,FS1,PosInts0_Bg_low, PosInts0_Bg_mid={},{},{},{},{},{},{},{}
#        ### ==== Prepare Average Spectrum of positions. === ####
#                print('Taking mean of {2} files for Sample: {0} of group {1} and fitting.'.format(sID,sGrp,len(grp)))
#                for idx,row in grp.iterrows():
#                    fp,Pos = row.Filepath, row.SamplePos
#                    FileName = os.path.splitext(os.path.basename(fp))[0]
#                    DestDir.mkdir(parents=True,exist_ok=True) 
#                    DestGrpDir.mkdir(parents=True,exist_ok=True)
##                    FileHelper.FileOperations.make_path(DestDir),FileHelper.FileOperations.make_path(DestGrpDir)
#                    try:
#                        w, i = np.loadtxt(fp, usecols=(0, 1), unpack=True)
#                        
##                        pd.read_csv(fp,sep='\t',names=['Frequency','Intenity_{0}'.format(Pos)]).set_index('Frequency')
#        #                i_Bg = SpectrumAnalyzer(w,i,FileName).S()[0]
#                        try:
#                            SpecInit = SpectrumAnalyzer(w,i,FileName)
#                            i1_Bg, w1_Bg, i_bg, w_bg  = SpecInit.i1_blcor, SpecInit.w1,SpecInit.i_blcor,SpecInit.w
#                            SpecInit_2nd = SpectrumAnalyzer(w,i,FileName,freqr_2nd[0],freqr_2nd[1])
##                            SpecInit_2nd = SpectrumAnalyzer(w,i,FileName,freqr_2nd[0],freqr_2nd[1])
#                            i1_Bg_2nd, w1_Bg_2nd, i_bg_2nd, w_bg_2nd  = SpecInit_2nd.i1_blcor, SpecInit_2nd.w1,SpecInit_2nd.i_blcor,SpecInit_2nd.w
#                            
#                            SpecInit_low = SpectrumAnalyzer(w,i,FileName,freqr_low[0],freqr_low[1],RAMAN_bgCorr_Plot=True)
#                            i1_Bg_low, w1_Bg_low, i_bg_low, w_bg_low  = SpecInit_low.i1_blcor, SpecInit_low.w1,SpecInit_low.i_blcor,SpecInit_low.w
#                            
#                            SpecInit_mid = SpectrumAnalyzer(w,i,FileName,freqr_mid[0],freqr_mid[1],RAMAN_bgCorr_Plot=True)
#                            i1_Bg_mid, w1_Bg_mid, i_bg_mid, w_bg_mid  = SpecInit_mid.i1_blcor, SpecInit_mid.w1,SpecInit_mid.i_blcor,SpecInit_mid.w
#                        except:
#                            print('Spectrum initialization problem, CRITICAL!')
##                        print(len(w),len(i),len(i1_Bg),len(w1_Bg))
##                        DataOut = {'RamanShift' : w,'Int' : i}
#                        PosRS0.update({'RamanShift_%s'%Pos : w})
#                        PosInts0.update({'%s'%FileName : i })
#                        ind1,ind = (w1_Bg > norm_window[0]) & (w1_Bg < norm_window[1]), (w > norm_window[0]) & (w < norm_window[1])
##                        ind1_2nd,ind_2nd = (w1_Bg_2nd > norm_window_2nd[0]) & (w1_Bg_2nd < norm_window_2nd[1]), (w > norm_window_2nd[0]) & (w < norm_window_2nd[1])
##                         < norm_window[1]
#                        norm= 1/i1_Bg[ind1].max()
##                       normFS,normi = 1/i_bg[ind].max(),1/i[ind].max()
##                        norm_2nd,normFS_2nd,normi_2nd = 1/i1_Bg_2nd[ind1_2nd].max(),1/i_bg_2nd[ind_2nd].max(),1/i[ind_2nd].max()
#                        FS1.update({'raw_{0}_{1}'.format(FileName,grNm) : i,'raw_norm_{0}_{1}'.format(FileName,grNm) : i*norm, 'despiked_{0}_{1}'.format(FileName,grNm)  : i_bg, 'despiked_norm_{0}_{1}'.format(FileName,grNm)  : i_bg*norm})
#                        
#                        PosInts0_Bg.update({'%s_Bg'%FileName : i1_Bg*norm })
#                        PosInts0_Bg_2nd.update({'%s_Bg'%FileName : i1_Bg_2nd*norm})
#                        PosInts0_Bg_low.update({'%s_Bg'%FileName : i1_Bg_low*norm})
#                        PosInts0_Bg_mid.update({'%s_Bg'%FileName : i1_Bg_mid*norm})
#                        
#                    except Exception as e:
#                        print('DATA Problem %s, %s:'%(UgrNm,grNm),e)
#                        continue 
#                    PosRS,PosInts,PosInts_Bg,FS= pd.DataFrame(PosRS0),pd.DataFrame(PosInts0),pd.DataFrame(PosInts0_Bg),pd.DataFrame(FS1)
#                    PosInts_Bg_2nd = pd.DataFrame.from_dict(PosInts0_Bg_2nd,orient='index').transpose().iloc[0:len(w1_Bg_2nd)]
#                    PosInts_Bg_low = pd.DataFrame.from_dict(PosInts0_Bg_low,orient='index').transpose().iloc[0:len(w1_Bg_low)]
#                    PosInts_Bg_mid = pd.DataFrame.from_dict(PosInts0_Bg_mid,orient='index').transpose().iloc[0:len(w1_Bg_mid)]
#                    
##                print(PosInts)    
#                PosInts = PosInts.assign(**{'%s_mean'%FileName.split('_')[0] : PosInts.mean(axis=1),'RamanShift' : w})
#                SampleBgmean_col = '{0}_Bg_mean_{1}'.format(sID.split('_')[0],len(PosInts_Bg.columns))
#                despiked_norm_bg_data_out_columns = [i for i in FS.columns if sGrp in i and 'despiked_norm' in i and not 'raw' in i] 
#                despiked_norm_bg_data_out_name = 'mean_norm_{0}_bl_{1}'.format(sID.split('_')[0],len(despiked_norm_bg_data_out_columns))
#
#                FS = FS.assign(**{despiked_norm_bg_data_out_name : FS.loc[:,despiked_norm_bg_data_out_columns].mean(axis=1),
#                            'mean_raw_%s'%sID.split('_')[0] :  FS.loc[:,[i for i in FS.columns if sGrp in i and 'raw' in i and not 'norm' in i and not 'despiked' in i]].mean(axis=1),
#                            'mean_raw_despiked_%s'%sID.split('_')[0] :  FS.loc[:,[i for i in FS.columns if sGrp in i and 'despiked' in i and not 'norm' in i]].mean(axis=1),
#                            'mean_raw_norm_%s'%sID.split('_')[0] :  FS.loc[:,[i for i in FS.columns if sGrp in i and 'raw_norm_' in i and not 'despiked' in i]].mean(axis=1),
#                            'RamanShift' : w})
##                FSOut = FS['mean_norm_%s_bl'%sID.split('_')[0]]
#                FS['mean_norm_out_%s'%sID.split('_')[0]] = SpectrumAnalyzer.subtract_baseline(FS['RamanShift'].values,FS[despiked_norm_bg_data_out_name].values,800,2000) 
#                FS['%s_rollingmean'%sID.split('_')[0]] = FS['mean_norm_out_%s'%sID.split('_')[0]].rolling(3).mean()
#
#                # ====== Running filter on means of collumns ====== #
#                Spec_mean_1st = scipy.signal.savgol_filter(PosInts_Bg.mean(axis=1).values, 13, 3, mode='nearest')
#                Spec_mean_2nd= scipy.signal.savgol_filter(PosInts_Bg_2nd.mean(axis=1).values, 13, 3, mode='nearest')
#                Spec_mean_low = scipy.signal.savgol_filter(PosInts_Bg_low.mean(axis=1).values, 13, 3, mode='nearest')
#                Spec_mean_mid = scipy.signal.savgol_filter(PosInts_Bg_mid.mean(axis=1).values, 13, 3, mode='nearest')
#
#                PosInts_Bg = PosInts_Bg.assign(**{SampleBgmean_col : Spec_mean_1st, 'RamanShift' : w1_Bg,
#                                                  '%s_std'%sID.split('_')[0] : PosInts_Bg.std(axis=1),
#                                                  '%s_count'%sID.split('_')[0] : PosInts_Bg.count(axis=1),})
#                PosInts_Bg_2nd = PosInts_Bg_2nd.assign(**{SampleBgmean_col :Spec_mean_2nd, 'RamanShift' : w1_Bg_2nd,
#                                                  '%s_std'%sID.split('_')[0] : PosInts_Bg_2nd.std(axis=1),
#                                                  '%s_count'%sID.split('_')[0] : PosInts_Bg_2nd.count(axis=1)})
#                PosInts_Bg_low = PosInts_Bg_low.assign(**{SampleBgmean_col : Spec_mean_low, 'RamanShift' : w1_Bg_low,
#                                                  '%s_std'%sID.split('_')[0] : PosInts_Bg_low.std(axis=1),
#                                                  '%s_count'%sID.split('_')[0] : PosInts_Bg_low.count(axis=1)})
#                PosInts_Bg_mid = PosInts_Bg_mid.assign(**{SampleBgmean_col : Spec_mean_mid,'RamanShift' : w1_Bg_mid,
#                                                  '%s_std'%sID.split('_')[0] : PosInts_Bg_mid.std(axis=1),
#                                                  '%s_count'%sID.split('_')[0] : PosInts_Bg_mid.count(axis=1)})
##                PosInts_Bg.to_excel(DestSmplDir+'\\%s_Baseline_mean.xlsx' %sID),PosInts_Bg_2nd.to_excel(DestSmplDir+'\\%s_2nd_Baseline_mean.xlsx' %sID)
#                FS.to_excel(DestExtraPlots.joinpath('fullspectrum_%s.xlsx' %sID))
#                PosInts_Bg.to_excel(DestExtraPlots.joinpath('%s_1st-order_raw_norm.xlsx'%sID))
#                PosInts_Bg_2nd.to_excel(DestExtraPlots.joinpath('%s_2nd-order_raw_norm.xlsx'%sID))
#                PosInts_Bg_low.to_excel(DestExtraPlots.joinpath('%s_low_raw_norm.xlsx'%sID))
#                PosInts_Bg_mid.to_excel(DestExtraPlots.joinpath('%s_mid_raw_norm.xlsx'%sID))
#                # ====== Make RAW data plots ====== #
#                FitRAMAN.raw_data_spectra_plot(sID,sGrp,FS,PosInts_Bg,PosInts_Bg_low,PosInts_Bg_mid,PosInts_Bg_2nd,DestExtraPlots)
#                # ====== Start Fitting procedure ====== #
#                out,comps,FitPars,FitData,init = SpectrumAnalyzer.Fit_VoigtModel_PyrCarbon(PosInts_Bg['RamanShift'].values,PosInts_Bg[SampleBgmean_col].values,'%s_mean'%sID,FitModel_1st='6peaks, Si_substrate',PreFit = False)
##in#                 Fit_VoigtModel_PyrCarbon(x,y,FileName,FitModel_1st='6peaks, Si_substrate')
##                out,comps,FitPars,FitData,init = SpectrumAnalyzer(PosInts_Bg['RamanShift'].values,PosInts_Bg[SampleBgmean_col].values,'%s_mean'%sID).Fit_VoigtModel_PyrCarbon('%s_mean'%sID,FitModel_1st=FitModPeaks)
#                out_2nd,comps_2nd,FitPars_2nd,FitData_2nd,init_2nd = SpectrumAnalyzer(PosInts_Bg_2nd['RamanShift'].values,PosInts_Bg_2nd[SampleBgmean_col].values,'%s_mean'%sID,
#                                                                                      freqr_2nd[0],freqr_2nd[1]).Fit_VoigtModel_PyrCarbon_2ndOrder('%s_mean'%sID)
#                 #%%
#              
#                FitPars['Date_script_run'] = pd.to_datetime(pd.datetime.now())
#                FitPars.fillna(0,inplace=True)
#                FitPars_2nd.fillna(0,inplace=True)
##                out,comps,FitPars,FitData,init = SpectrumAnalyzer(RaSh,Int,i).Fit_VoigtModel_PyrCarbon(metadata['SampleID'])
##                SpectrumAnalyzer(PosInts_Bg['RamanShift'].values,PosInts_Bg[SampleBgmean_col].values,'%s_mean'%sID,norm_window_2nd[0],norm_window_2nd[1]).plot_fit_output(out,comps,FitPars,FitData,DestSmplDir,'%s_mean'%sID,'mean')
##                Fit_VoigtModel_PyrCarbon_2ndOrder(self,SampleID):
##                SpectrumAnalyzer(w,i,'%s_mean'%sID,2100,3500).Fit_VoigtModel_PyrCarbon_2ndOrder(sID)
##                N2_bg = SpectrumAnalyzer(self.Rash,self.Int,self.Filename,2100,3000).subtract_bg(sID)
##                PosInts_Bg = PosInts_Bg.assign(**{'%s_Bg_mean'%FileName.split('_')[0] : PosInts_Bg.mean(axis=1),'RamanShift_%s_Bg'%FileName.split('_')[0] : w_Bg})
#            #%%
#                FitRAMAN.fit_spectrum_plot(sID, DestPlotDir, SampleBgmean_col, FitData, FitModPeaks, FitData_2nd,comps, comps_2nd,out, out_2nd, 
#                          FitPars, FitPars_2nd, plot_Annotation = True, plot_Residuals = True)
#                #%%
##                pd.concat([FitPars,FitPars_2nd],axis=1).to_hdf()
#                RResult = pd.concat([RResult,pd.concat([FitPars,FitPars_2nd],axis=1)])
##                RResult.to_excel(DestFitCompsDir.joinpath('%s_PARS.xlsx'%(sID)))
#                FitData.to_excel(DestFitCompsDir.joinpath('%s_COMPS1.xlsx'%(sID))), FitData_2nd.to_excel(DestFitCompsDir.joinpath('%s_COMPS_2nd.xlsx'%(sID)))
##                PosInts_Bg[SampleBgmean_col]
#                GrOut = GrOut.assign(**{'%s_Bg_mean'%sID : PosInts_Bg[SampleBgmean_col],'%s_mean_Fit'%sID : FitData['I_model4Voigt']}).dropna(axis=0)
#                GrOut2 = GrOut2.assign(**{'%s_Bg_mean'%sID : PosInts_Bg_2nd[SampleBgmean_col],'%s_mean_Fit'%sID : FitData_2nd['I_model4Voigt']
#                                        ,'%s_RamanShift '%sID : PosInts_Bg_2nd.RamanShift }).dropna(axis=0)
#                GrOutFS = GrOutFS.assign(**{'%s'%sID.split('_')[0] : FS['mean_norm_out_%s'%sID.split('_')[0]], '%s_rolmean'%sID.split('_')[0] : FS['%s_rollingmean'%sID.split('_')[0]] ,'RamanShift' : FS['RamanShift']})
##                PosInts_Bg.to_hdf(DBpath,key = 'RAMAN/%s/%s/FittedSpectrum'%(sGrp,sID), mode = 'a',format = 'table')
##                PosInts_Bg.to_hdf(DBpath,key = 'RAMAN/%s/%s/FittedSpectrum_2ndOrder'%(sGrp,sID), mode = 'a',format = 'table')
##                FS.to_hdf(DBpath,key = 'RAMAN/%s/%s/FullSpectrum'%(sGrp,sID), mode = 'a',format = 'table')
##                with FitRAMAN.DB_write as HDF:
##                    item = HDF['RAMAN/%s/%s/%s'%(SampleGrp,SampleID,SamplePos)]
##                    g1 = HDF.create_group('RAMAN/%s/%s/%s'%(sGrp,sID))
##                    g1.create_dataset('Spectrum',data=FS)
#            try:
#                GrOut = GrOut.assign(**{'RamanShift' : w1_Bg})
#            except Exception as e:
#                print('Can not assign GrOut len w1_Bg ({0})'.format(len(w1_Bg)),e)
##            GrOut2 = GrOut2.assign(**{'RamanShift' : w1_Bg_2nd})
#            GrOut.to_excel(DestGrpDir.joinpath('All_1st-order_Baseline_mean_%s.xlsx' %sGrp))
#            GrOut2.to_excel(DestGrpDir.joinpath('All_2nd-order_Baseline_mean_%s.xlsx' %sGrp))
#            GrOutFS.to_excel(DestGrpDir.joinpath('FullSpectrum_mean_%s.xlsx' %sGrp))
##            a.rename(columns=dict(zip(a.columns,[i.split('_')[-1] for i in a.columns]))).to_excel(DestDir+'\\DW'+'\\DW_FullSpectrum_mean.xlsx')
#            RResult.to_excel(DestGrpDir.joinpath('AllPars_%s.xlsx' %sGrp)) 
##            RResult.to_hdf(DBpath,key = 'RAMAN/%s/FitPars'%(sGrp), mode = 'a',format = 'table')
#            AllResult = pd.concat([AllResult,RResult])
#    #        figBG,axBG = plt.subplots(1,1,figsize=(12,12))
#    #        axBG.plot(PosRS.iloc[:,0],PosInts_Bg['%s_Bg_mean'%FileName.split('_')[0]],label='Bg 1st' )
#    #        yMnBg = RAMAN_subtract_baseline(PosRS.iloc[:,0].values,PosInts['%s_mean'%FileName.split('_')[0]].values,freqMin,freqMax)
#    #        axBG.plot(PosRS.iloc[:,0],yMnBg,label='Mean 1st' )
#    #        axBG.legend()
#    #            ,'RamanShift' : PosRS.iloc[:,0]})
#    #            ,PosRS.assign(**{'RamanShift_mean' : PosRS.mean(axis=1)})
#        try:    
#            read_ovv = pd.read_excel(RAMAN_dir.joinpath('RAMAN_OVV.xlsx'),index_col=[0])
#            read_ovv = read_ovv.update(AllResult.reset_index())
#            read_ovv.to_excel(RAMAN_dir.joinpath('RAMAN_OVV.xlsx'))
#        except Exception as e:
#            if 'PermissionError' == e:
#                AllResult.reset_index().to_excel(RAMAN_dir.joinpath('RAMAN_OVV_1.xlsx'))
##        AllResult.reset_index().to_excel()
#        '''ID/IG	ID3/IG	G_center	D_center	D4_center	D3_center'''
##        AllResult.reset_index().to_hdf(DBpath,key = 'RAMAN/%s/FitPars_OVV' %SampleGroupDef, mode = 'a',format = 'table')
#        print('Overview: %s' %(RAMAN_dir.joinpath('RAMAN_OVV_%s.xlsx'%SampleGroupDef)))
#        
#def fit_each_sample(RFrow):
#    RAMAN_DB = FileHelper.FindExpFolder('RAMAN').DestDir.joinpath('RAMAN_DB.hdf5')
#    
#    with h5py.File(RAMAN_DB,'w',libver='latest') as hf:
#        metadata = dict(zip(['Filepath', 'Filename','SampleID' , 'SamplePos' , 'SampleGroup', 'FileCreation', 'FileMod','DestDir','FileHash'],sOut))
#        try:
#            RaSh, Int = np.loadtxt(RFrow.FilePath, usecols=(0, 1), unpack=True)
#        except Exception as e:
#            print('DATA Problem: ',e)
#            RaSh, Int  = [],[]
##                continue 
##            with h5py.File(RAMAN_DB,'a') as db:
##                print(metadata)
#        HF_subdir = 'RAMAN/%s/%s/%s'%(metadata['SampleGroup'],metadata['SampleID'],metadata['SamplePos'])
#        try:
#            g = hf.create_group(HF_subdir)
#        except:
#            g = hf.create_group(HF_subdir+'_repeat')
##                g=db.create_group(split[0][0:2])
##                gg= g.create_group(split[0])
##                ggg = gg.create_group(i)
##                gggg= ggg.create_group(split[1])
##                print(metadata)
#        d = g.create_dataset('RamanShift_raw',data=RaSh)
##                    d = g.create_dataset('Int_Bg',data=SpectrumAnalyzer(RaSh,Int,i).subtract_baseline())
#        d = g.create_dataset('Int_Bg_despike',data=SpectrumAnalyzer(RaSh,Int,i).i_blcor)
#        out,comps,FitPars,FitData,init = SpectrumAnalyzer(RaSh,Int,i).Fit_VoigtModel_PyrCarbon(metadata['SampleID'])
#        SpectrumAnalyzer(RaSh,Int,i).plot_fit_output(out,comps,FitPars,FitData,DestDir,metadata['SampleID'],metadata['SamplePos'])
##                    store = pd.HDFStore('RAMAN_DB')
##                    store.append(HF_subdir+'/FIT_DATA',FitData,complib='zlib', complevel=5)
##                    store.append(HF_subdir+'/FIT_PARS',FitPars,complib='zlib', complevel=5)
##                    store.close()
##                store.select(HF_subdir+'/FIT_DATA',"columns='G_peak'")
##                d = g.create_dataset('FitData',data=FitData)
##                d = g.create_dataset('FitPars',data=FitPars)
##                d = g.create_dataset('FitData',data=FitData)
##                print(out)
##               plot_fit_output(self,out,FitPars,FitData,DestDir,SampleID,Pos):
#        d = g.create_dataset('Intensity',data=Int)
#        d.attrs.update(metadata)    
        #ovv = pd.read_csv(RAMAN_dir+'\\RAMAN_OVV.csv')
#        ParsOut.reset_index().to_excel(RAMAN_DestDir+'\\ParsOut.xlsx')
#        return RResult
        #%%
def run_selection():
    run = input('Want to start the fitting run?')
    sys.path.append(Path(__file__).parent.parent)
    try:
        FindExpText = str(inspect.getsource(FileHelper.FindExpFolder)).encode('utf-8')
#    pytext =
        pytext = FileHelper.FileOperations.mylocal_read_text(Path(__file__)) + str(FindExpText)
    except Exception as e:
        pytext = 'test'
        
    FileHash = hashlib.md5(str(pytext).encode('utf-8')).hexdigest()
    force_reindex = 0
    print('Hash:', FileHash)
    if 'y' in run or run == 'yes':
        PostProcess = False
        orgRFs = OrganizeRAMANFiles().ovv()
#        orgRFs.sort_values(by='FileCreation')
        recent_groups =[i for i in run.split() if i in orgRFs.SampleGroup.unique()]
#        recent_groups = orgRFs.sort_values(by='FileCreation').tail(30).SampleGroup.unique()
#        x= ['CG','JS','KLN','SD','LM']
#        recent_groups = ['PPY','KLN','JS','MK']
        recent_groups = ['JS']
#        recent_groups2 = ['KL','VG']
        print(f'Running groups: {recent_groups}')
        org_recent = orgRFs.loc[orgRFs.SampleGroup.str.contains(('|'.join)(recent_groups))]
#        .query('SampleID == "DW19"').query('SampleID == "KLNPPy2"')
#        org_recent = orgRFs.query('SampleID == "JOS12"')
        if run == 'yall':
            org_recent = orgRFs
        FitRAMAN().plot_RAMAN(org_recent)
#        MultiMain(org_recent)
        if PostProcess == True:
            RamanPostProcessing('DW').PostPlot()
    elif 'index'in run:
        orgRFs = OrganizeRAMANFiles().ovv()
        print(orgRFs.SampleGroup.unique())
        
def index_selection(RamanIndex,**kwargs):
    keys = kwargs.keys()
    if 'groups' in keys:
#        if 'str' in type(kwargs['groups']):
        index_selection = RamanIndex.loc[RamanIndex.SampleGroup.str.contains('|'.join(kwargs['groups']))]
    if 'run' in keys:
        runq = kwargs.get('run')
        if 'recent' in runq:
            grp = RamanIndex_all.sort_values('FileCreationDate',ascending=False).FileCreationDate.unique()[0]
            
            index_selection  =RamanIndex_all.loc[RamanIndex.FileCreationDate == grp]
            index_selection = index_selection.assign(**{'DestDir' : [Path(i).joinpath(grp.strftime('%Y-%m-%d')) for i in index_selection.DestDir.values]})
            
    return index_selection
#%%
if __name__ == "__main__":
#    pass
    runq = input('run raman?')
    if 'y' in runq:
#        try:
#            if not RamanIndex.empty:
#                print('Raman Index ready')
#        except:
#            print('Raman re-indexing')
#            RamanIndex_all = OrganizeRamanFiles().index
#            SampleSelection.Series_Porhp_SiO2
#            RamanIndex = index_selection(RamanIndex_all,groups=['DW','JOS','MK','LK'])
#            RamanIndex = index_selection(RamanIndex_all,groups=['JOS'])
##            RamanSer = RamanIndex.loc[RamanIndex.SampleID.isin(SampleSelection.Series_Porhp_SiO2['sIDs'])]
##            RamanSer['DestDir'] = [i.joinpath('Porph_SiO2') for i in RamanSer['DestDir'].values]
        RamanIndex_all = OrganizeRamanFiles().index
        RamanIndex = index_selection(RamanIndex_all,run= runq,groups=['JS'])
        RamanLoop.run_index(RamanIndex)
    elif runq == 'n':
        pass
    else:
        try:
            if not RamanIndex.empty:
                print('Raman Index ready')
        except:
            print('Raman re-indexing')
            RamanIndex_all = OrganizeRamanFiles().index
            
            RamanIndex = index_selection(RamanIndex_all,groups=['JOS'])
    #    
#class FitRAMAN:
#    """Takes in the Organized Raman Files, performs the fit over the mean of the several positions of the same SampleID
#        and performs the plot of raw data and fitting for 1st and 2nd order"""
##    DestDir = FileHelper.FindExpFolder('RAMAN').DestDir
##    orgRFs = OrganizeRAMANFiles().ovv()
#    
#    def __init__(self):
#        pass
#        #        self.DBpath = FileHelper.FindExpFolder('RAMAN').DestDir.joinpath('RAMAN_DB.hdf5')
##        self.orgRFs = orgRFs
##    @staticmethod
##    def DB_path(self):
#        
#    @staticmethod
#    def DB_read(self):
#        self.DBread = h5py.File(FileHelper.FindExpFolder('RAMAN').DestDir.joinpath('RAMAN_DB.hdf5'),'r')
#    @staticmethod
#    def DB_write(self):
#        self.DBwrite = h5py.File(FileHelper.FindExpFolder('RAMAN').DestDir.joinpath('RAMAN_DB.hdf5'),'w',libver='latest')
##    @staticmethod
##    def DB_path(self):
##        return os.path.join( FileHelper.FindExpFolder('RAMAN').DestDir,'RAMAN_DB.hdf5')
##        HDF = h5py.File(os.path.join(DestDir,'RAMAN_DB.hdf5'),'r')
#    def Fit_Mean(self):
##        %%
#        HDF = FitRAMAN.DB_read()
#        for SampleGrp in [i for i in HDF['RAMAN/'].keys()]:
#            for SampleID in [i for i in HDF['RAMAN/%s'%SampleGrp].keys()]:
#                for SamplePos in [i for i in HDF['RAMAN/%s/%s'%(SampleGrp,SampleID)].keys()]:
#                    print(SamplePos)
#                    item = HDF['RAMAN/%s/%s/%s'%(SampleGrp,SampleID,SamplePos)]
#                    print(item)
#                RAMAN_dir,RAMAN_DestDir = FileHelper.FindExpFolder('RAMAN').DataDir,FileHelper.FindExpFolder('RAMAN').DestDir
#    freqMin,freqMax,plot_Components,plot_Annotation,plot_Residuals,GammaVary,RAMAN_bgCorr_Plot = 800,2000,True,True,True,True,False
#DF,RDB = OrganizeRAMANFiles().ovv()
#    ParsOut = plot_RAMAN(FileHelper.FindExpFolder('RAMAN').DataDir,freqMin,freqMax,plot_Components,plot_Annotation,plot_Residuals,GammaVary,RA
#    destdir, DBpath, 
#    TODO FitModels later