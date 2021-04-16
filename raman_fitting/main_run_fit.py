#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:49:20 2020

@author: DW
"""
import sys
from collections import namedtuple
from operator import itemgetter
from pathlib import Path

from functools import reduce
from itertools import chain
from operator import add

import numpy as np
import hashlib

import pandas as pd
from scipy import signal
from scipy.stats import linregress


#from .raman_fitting 

# from config import config

if __name__ == "__main__":

    from deconvolution_models import fit_models
    from indexer.indexer import OrganizeRamanFiles
    from plotting import raw_data_export, fit_spectrum_plot


else:
    from raman_fitting.deconvolution_models import fit_models
    from raman_fitting.indexer.indexer import OrganizeRamanFiles
    from raman_fitting.plotting import raw_data_export, fit_spectrum_plot




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
#        DestDir = sGrp_grp.DestDir.unique()[0]
        DestGrpDir = Path(sGrp_grp.DestDir.unique()[0])
#        DestDir.joinpath(sGr)
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
            for nm, sID_grp in sGrp_grp.groupby(list(GrpNames.sGrp_cols[1:])):
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
                
                results_1st,results_2nd = fit_models.start_fitting(fitting_specs)
                
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
    Operations done in this class: read-raw-spectrum > savgol_filter > 
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
    
#%%           
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
         
#
class Despike():
    ''' Despiking algorith from reference literature:
    Let Y1;...;Yn represent the values of a single Raman spectrum recorded at equally spaced wavenumbers.
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
      
        recent_groups =[i for i in run.split() if i in orgRFs.SampleGroup.unique()]  

        print(f'Running groups: {recent_groups}')
        org_recent = orgRFs.loc[orgRFs.SampleGroup.str.contains(('|'.join)(recent_groups))]
        if run == 'yall':
            org_recent = orgRFs
        FitRAMAN().plot_RAMAN(org_recent)

        if PostProcess == True:
            RamanPostProcessing('DW').PostPlot()
    elif 'index'in run:
        orgRFs = OrganizeRAMANFiles().ovv()
        print(orgRFs.SampleGroup.unique())
        
def index_selection(RamanIndex_all,**kwargs):
    keys = kwargs.keys()
    if 'groups' in keys:
        if kwargs['groups']:
            index_selection = RamanIndex_all.loc[RamanIndex_all.SampleGroup.str.contains('|'.join(kwargs['groups']))]
        else:
            index_selection = RamanIndex_all
    if 'run' in keys:
        runq = kwargs.get('run')
        if 'recent' in runq:
            grp = RamanIndex_all.sort_values('FileCreationDate',ascending=False).FileCreationDate.unique()[0]
            
            index_selection  =RamanIndex_all.loc[RamanIndex_all.FileCreationDate == grp]
            index_selection = index_selection.assign(**{'DestDir' : [Path(i).joinpath(grp.strftime('%Y-%m-%d')) for i in index_selection.DestDir.values]})
            
    return index_selection
#%%
if __name__ == "__main__":

    runq = input('run raman? (enter y for standard run):\n')
    if 'y' in runq:

        RamanIndex_all = OrganizeRamanFiles().index
        RamanIndex = index_selection(RamanIndex_all,run= runq,groups=[])
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
            
            RamanIndex = index_selection(RamanIndex_all,groups=[])
