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



#from .raman_fitting 

# from config import config

if __name__ == "__main__":

    from deconvolution_models import fit_models
    from indexer.indexer import OrganizeRamanFiles
    from processing.cleaner import SpectrumCleaner
    from processing.prepare_mean_spectrum import PrepareMean_Fit
    from processing.spectrum_template import Spectrum
    
    from export.plotting import raw_data_export, fit_spectrum_plot

else:
    
    from raman_fitting.deconvolution_models import fit_models
    from raman_fitting.indexer.indexer import OrganizeRamanFiles
    
    from raman_fitting.processing.cleaner import SpectrumCleaner
    from raman_fitting.processing.prepare_mean_spectrum import PrepareMean_Fit
    from raman_fitting.processing.spectrum_template import Spectrum
    
    from raman_fitting.export.plotting import raw_data_export, fit_spectrum_plot



# def namedtuplemerge(*args):
#     cls = namedtuple('_'.join(arg.__class__.__name__ for arg in args), reduce(add, (arg._fields for arg in args)))
#     return cls(*chain(*args))

#%%

def _testing():
    rr = RamanLoop()

class RamanLoop():
    ''' takes an index of a pd.DataFrame as input,
        runs the fitting loop over this index and exports
        plots and files.
    '''
    
    
    def __init__(self, RamanIndex = pd.DataFrame(), run_mode = 'normal' ):
        self.spectrum = Spectrum()
        self.index = RamanIndex
        self.run_mode = run_mode
        
        self.run_delegator()
        
        
    def test_positions(self, sGrp_grp,nm, grp_cols = ['FileStem','SamplePos','FilePath']):
#        grp_cols = ['FileStem','SamplePos','FileCreationDate']
        if sGrp_grp.FileStem.nunique() != sGrp_grp.SamplePos.nunique():
            print(sGrp_grp[grp_cols])
            print(f'Unique files and positions not matching for {nm}')
            return sGrp_grp.groupby(grp_cols),grp_cols
        else:
            return sGrp_grp.groupby(grp_cols),grp_cols
        
    def add_make_destdirs(self, sGr, sGrp_grp):
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
    
    def test_spectra_lengths(self, sample_spectra):
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

    def run_delegator(self):
        
        assert type(self.index) == type(pd.DataFrame())
        
        if self.run_mode == 'normal':
            if not self.index.empty:
                self.run_index()
            else:
                pass
                # info raman loop finished because index is empty
        elif 'testing' in self.run_mode:
            # TODO get testing from index and run
            pass
        else:
            pass # warning run mode not understood
        
            
                    
    def run_index(self):
        GrpNames = self.spectrum.grp_names
#        info_cols = sGrp_cols+ sPos_cols + spectrum_cols + spectrum_info_cols
        spec_template = self.spectrum.template
        all_spectra = {}
        all_index = []
        FitParams1, FitParams2 = [], []
        for grpnm, sGrp_grp in self.index.groupby(GrpNames.sGrp_cols[0]):
            all_index = []
            for nm, sID_grp in sGrp_grp.groupby(list(GrpNames.sGrp_cols[1:])):
                sGr, (sID, sDate) = grpnm, nm
                
                sGr_out = dict(zip(GrpNames.sGrp_cols,(grpnm,)+nm))
                export_info_out = self.add_make_destdirs(sGr,sID_grp)
                sample_pos_grp,sPos_cols = self.test_positions(sID_grp,nm,list(GrpNames.sPos_cols))
                
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
                    sample_spectrum_position_info = spec_template(**{**sGr_out, **export_info_out, **sPos_out, **spectrum_out})
                    
    #                dict(zip(GrpNames.all,nm+meannm+(ramanshift, intensity_raw, intensity, len(ramanshift)))
    #                sample_spectrum_position_info = Spectrum(**dict(zip(GrpNames.all,nm+meannm+(ramanshift, intensity_raw, intensity, len(ramanshift)))))
                    
                    sample_spectra.append(sample_spectrum_position_info)
                sample_spectra = self.test_spectra_lengths(sample_spectra)
                speclst = PrepareMean_Fit.subtract_baseline(sample_spectra)
                fitting_specs = PrepareMean_Fit.calc_mean_from_spclst(speclst) # TODO return mean of spectra 
                
                raw_data_export(fitting_specs) # TODO RAW data export and plotting
                
                results_1st,results_2nd = fit_models.start_fitting(fitting_specs)
                
                pars1,pars2 = RamanExport().export_fitting_plotting_peak(results_1st,results_2nd )
                FitParams1.append(pars1), FitParams2.append(pars2)
            index = RamanExport().export_FitParams_Grp(FitParams1, FitParams2, export_info_out, grpnm,sID)
            all_index.append(index)
            pars_index = pd.DataFrame(*all_index,columns=list(GrpNames.sGrp_cols[0:2] +('PeakModel','DestPars')))
            pars_index.to_excel( export_info_out.get('DestGrpDir').joinpath(f'{sGr}_index.xlsx'))
        
class RamanExport():
    
    def __init__(self):
        pass
    
    def export_FitParams_Grp(self,FitParams1, FitParams2, export_info_out, grpnm, sID):
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
                
    # Exporting and Plotting
    
    def export_fitting_plotting_peak(self, results_1st, results_2nd):
        pars1, pars2 = [], []
        for peak2,res2_peak_spec  in results_2nd.items():
            self.export_xls_from_spec(res2_peak_spec)
            pars2.append(res2_peak_spec.FitParameters)
            for peak1,res1_peak_spec in results_1st.items():
                self.export_xls_from_spec(res1_peak_spec) 
                try:
                    fit_spectrum_plot(peak1,res1_peak_spec,res2_peak_spec, plot_Annotation = True, plot_Residuals = True)
                except Exception as e:
                    print(f'Error fit_spectrum_plot:{peak1}, {res1_peak_spec.raw_data_col}.\n {e}'  )
                pars1.append(res1_peak_spec.FitParameters)
        return pd.concat(pars1,sort=False), pd.concat(pars2,sort=False)
                
    def export_xls_from_spec(self, res_peak_spec):
        sID = res_peak_spec.extrainfo.SampleID.unique()[0]
        peak_destpath = res_peak_spec.extrainfo.DestFittingComps.unique()[0].joinpath(f'Model_{res_peak_spec.peak_model}_{sID}')
        peak_destpath_extra = res_peak_spec.extrainfo.DestFittingComps.unique()[0].joinpath(f'Extra_{res_peak_spec.peak_model}_{sID}')
        res_peak_spec.FitComponents.to_excel(peak_destpath.with_suffix('.xlsx'), index=False)
        res_peak_spec.extrainfo.to_excel(peak_destpath_extra.with_suffix('.xlsx'), index=False)

             
    
        
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

    # runq = input('run raman? (enter y for standard run):\n')
    runq = 'y'
    if 'y' in runq:

        RamanIndex_all = OrganizeRamanFiles().index
        RamanIndex = index_selection(RamanIndex_all,run= runq,groups=[])
        
        RamanLoop(RamanIndex)
        
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
