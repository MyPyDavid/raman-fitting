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
import sqlite3


#from .raman_fitting 

# from config import config

if __name__ == "__main__":

    from indexer.indexer import OrganizeRamanFiles
    # from processing.cleaner import SpectrumCleaner
    from processing.spectrum_template import SpectrumTemplate
    from processing.spectrum_constructor import SpectrumDataLoader, SpectrumDataCollection
    
    from export.plotting import raw_data_export, fit_spectrum_plot
    from deconvolution_models.fit_models import InitializeModels, Fitter
    from raman_fitting.export.exporter import Exporter
    from config import config

else:
    
    from raman_fitting.indexer.indexer import OrganizeRamanFiles
    
    # from raman_fitting.processing.cleaner import SpectrumCleaner
    from raman_fitting.processing.spectrum_constructor import SpectrumDataLoader, SpectrumDataCollection
    
    # from raman_fitting.export.plotting import raw_data_export, fit_spectrum_plot



# def namedtuplemerge(*args):
#     cls = namedtuple('_'.join(arg.__class__.__name__ for arg in args), reduce(add, (arg._fields for arg in args)))
#     return cls(*chain(*args))

#%%
RamanDataDir = config.DATASET_DIR

def _testing():
    rr = RamanLoop()
    
    
class RamanDB:
    
    
    def __init__(self):
        self.dbpath = config.RESULTS_DIR.joinpath('sqlite.db')
    
    def conn(self):
        self.conn = sqlite3.connect(self.dbpath)
        
    

class RamanLoop():
    ''' takes an index of a pd.DataFrame as input,
        runs the fitting loop over this index and exports
        plots and files.
    '''
    
    def __init__(self, RamanIndex = pd.DataFrame(), run_mode = 'normal' ):
        self.spectrum = SpectrumTemplate()
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
    
    def run_delegator(self):
        
        assert type(self.index) == type(pd.DataFrame())
        if self.run_mode == 'normal':
            if not self.index.empty:
                self.run_index()
            else:
                pass
                # info raman loop finished because index is empty
        elif 'DEBUG' in self.run_mode:
            try:
                self.run_index()
            except Exception as e:
                print('Error in DEBUG run: ', e)
            # TODO get testing from index and run
            pass
        else:
            pass # warning run mode not understood
    
    def set_models(self):
        self.InitModels  = InitializeModels()
    
    def run_index(self):
        self.set_models()
        GrpNames = self.spectrum.grp_names
#        info_cols = sGrp_cols+ sPos_cols + spectrum_cols + spectrum_info_cols
        spec_template = self.spectrum.template
        all_spectra = {}
        all_index = []
        FitParams1, FitParams2 = [], []
        export_collect = []
        for grpnm, sGrp_grp in self.index.groupby(GrpNames.sGrp_cols[0]): # Loop over SampleGroups 
            all_index = []
            for nm, sID_grp in sGrp_grp.groupby(list(GrpNames.sGrp_cols[1:])):# Loop over SampleIDs within SampleGroup
                sGr, (sID, sDate) = grpnm, nm
                
                sGr_out = dict(zip(GrpNames.sGrp_cols,(grpnm,)+nm))
                export_info_out = self.add_make_destdirs(sGr,sID_grp)
                sample_pos_grp,sPos_cols = self.test_positions(sID_grp,nm,list(GrpNames.sPos_cols))
                
                sample_spectra = []
                for meannm, meangrp in sample_pos_grp:# Loop over individual Sample positions (files) from a SampleID
#                    print(meannm)

                    sPos_out = dict(zip(GrpNames.sPos_cols,meannm))
                    _spectrum_position_info_kwargs =  {**sGr_out, **export_info_out, **sPos_out}

                    spectrum_data = SpectrumDataLoader(file = meannm[-1], run_kwargs = _spectrum_position_info_kwargs, ovv = meangrp)
                    # spectrum_data.plot_raw()
                    sample_spectra.append(spectrum_data)

                spectra_collection = SpectrumDataCollection(sample_spectra)
                ft = Fitter(spectra_collection,RamanModels = self.InitModels)
                rex = Exporter(ft)
                export_collect.append(rex)
            Exporter(export_collect)
   

             
    
        
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
        RamanIndex = index_selection(RamanIndex_all,run= runq,groups=['DW'])
        RL = RamanLoop(RamanIndex, run_mode ='normal')
        # self = RL
    elif 'test' in runq:
        RamanIndex_all = OrganizeRamanFiles().index
        RamanIndex = index_selection(RamanIndex_all,run= runq,groups=[])
        RL = RamanLoop(RamanIndex, run_mode ='DEBUG')
        self = RL
        
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
