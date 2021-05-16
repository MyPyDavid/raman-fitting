#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:48:22 2020

@author: zmg
"""
import sys
import hashlib

from pathlib import Path
from collections import namedtuple

import pandas as pd

import logging
import typing as t


_logger = logging.getLogger(__name__)


if __name__ == "__main__":
#        config.RESULTS_DIR
        # TODO !! fix and add local import for FindExpFolder, SampleIDstr and GetSampleID
        pass

# from ..config import config

__all__= ['OrganizeRamanFiles']

#%%


class OrganizeRamanFiles:   
    """Finds the RAMAN files in the top folder from config and creates an overview"""
    
    file_sample_cols = ['FileStem','SampleID','SamplePos','SampleGroup', 'FilePath']
    file_stat_cols = ['FileCreationDate', 'FileCreation','FileModDate', 'FileMod', 'FileHash']
    
    
    def __init__(self, reload_index = True, run_mode = 'normal', costum_datadir = Path()):
        self._reload_index = reload_index
        self._run_mode = run_mode
        self.choose_dirs()
        self.load_index()
        
#        OrganizeRamanFiles.index(self)
#        self.raman_data_files = OrganizeRAMANFiles.find_files()
#        self.ExpFiles = OrganizeRAMANFiles.find_files(FileHelper.FindExpFolder('RAMAN').DataDir)
#        self.ExpOVV = self.ovv(self.ExpFiles)
#        self.ExpDB = FileHelper.FindExpFolder(exp_method).DestDir.joinpath('RAMAN_DB.hdf5')
    
    def choose_dirs(self):
        
        if 'debug' in self._run_mode:
            DestDir = config.PACKAGE_ROOT.parent.joinpath('tests/test_results')
            RamanDataDir = config.PACKAGE_ROOT.parent.joinpath('tests/test_data')
            IndexFile = DestDir.joinpath('test_index.csv')
            
        else:
            DestDir = config.RESULTS_DIR
            RamanDataDir = config.DATASET_DIR
            IndexFile = config.INDEX_FILE
        
        if not RamanDataDir.is_dir():
            raise FileNotFoundError('This path to directory does not exist')

        if not DestDir.is_dir():
            DestDir.mkdir(exist_ok=True,parents=False)
            
        self.DestDir = DestDir
        self.RamanDataDir = RamanDataDir
        self.IndexFile = IndexFile
    
    # def _set_debug_paths(self):
        
        
    def find_files(self):
        RFs = list(self.RamanDataDir.rglob('*txt'))
        raman_files_raw = [i for i in RFs if not 'fail' in i.stem and not 'Labjournal' in str(i)]
        self.raman_files = raman_files_raw
    
    def _fsID(self,rf):
        try:
            _res = self.find_SampleID_position(rf)
        except Exception as e:
            _logger(f'Error fsid for {rf} \n{e}')
            _res = ()
            self._error_sids.append((rf,e))
        return _res
    
    @staticmethod
    def find_SampleID_position(ramanfilepath):
        ramanfile_stem  = ramanfilepath.stem

        if '_'  in ramanfile_stem:
            split = ramanfile_stem.split('_')
        elif ' ' in ramanfile_stem:
            split = ramanfile_stem.split(' ')
        else:
#            print(ramanfile_stem)
            split = ramanfile_stem.split('_')
            
        if 'SI' in ramanfile_stem.upper() or 'Si-ref' in ramanfile_stem: 
            position = 0
            sID = 'Si-ref'
        else:
            if len(split) == 1:
                sID = [SampleIDstr(split[0]).SampleID][0]
                position = 0
            elif len(split) == 2:
                sID = split[0]
                _pos_strnum = ''.join(i for i in split[1] if i.isnumeric())
                if _pos_strnum:
                    position = int(_pos_strnum)   
                else:
                    position = split[1]
                    
#                split = split + [0]
            elif len(split) >= 3:
                sID = [SampleIDstr('_'.join(split[0:-1])).SampleID][0]
                position = int(''.join(filter(str.isdigit,split[-1])))
#                split =[split_Nr0] + [position]
            elif  len(split) == 0:
                sID = SampleIDstr(split).SampleID
                position = 0
            else:
                 sID = [SampleIDstr(split[0]).SampleID][0]
                 if ''.join(((filter(str.isdigit,split[-1])))) == '':
                     sID = [ramanfile_stem]
                     position = 0
                 else:
                     position = int(''.join(filter(str.isdigit,split[-1])))

        sGrpID = ''.join([i for i in sID[0:3] if i.isalpha()])
        if 'Raman Data for fitting David' in ramanfilepath.parts:
            sGrpID = 'SH'    
#        RF_row_sIDs_out = 
        RF_row_sIDs_out = (ramanfile_stem, sID, position, sGrpID, ramanfilepath)
        return RF_row_sIDs_out
    
    @staticmethod
    def get_file_stats(ramanfilepath):
        fstat = ramanfilepath.stat()
        ct, mt = pd.to_datetime(fstat.st_ctime,unit='s'), pd.to_datetime(fstat.st_mtime,unit='s')
        ct_date, mt_date = ct.date(),mt.date()
        filehash = hashlib.md5(ramanfilepath.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
        filestat_out = ct_date, ct,mt_date, mt, filehash
        return filestat_out

    def make_index(self):
    #    ridx = namedtuple('Raman_index_row', file_sample_cols+file_stat_cols)
        self.find_files()
        self._error_sids = []
        RF_indexed = [(self._fsID(i)+self.get_file_stats(i)) for i in self.raman_files]
        RF_index_raw = pd.DataFrame(RF_indexed,columns = self.file_sample_cols+self.file_stat_cols).drop_duplicates(subset=['FileHash'])
        
        RF_index_raw = RF_index_raw.assign(**{'DestDir' : [self.DestDir.joinpath(sGrp) for sGrp in RF_index_raw.SampleGroup.to_numpy()]})
        
        self.index = RF_index_raw
    
    def export_index(self):
        if not self.index.empty:
            self.index.to_csv(self.IndexFile)
            _logger.info(f'Succesfully Exported Raman Index file to {config.INDEX_FILE}, with len({len(self.index)})')
    
    def load_index(self):
        if not self._reload_index:
            try:
                _index_load = pd.read_csv(self.IndexFile)
                _logger.info(f'Succesfully imported Raman Index file from {config.INDEX_FILE}, with len({len(_index_load)})')
                self.index = _index_load
            except:
                _logger.error(f'Error in load_index from {config.INDEX_FILE}, restarting make_index ... )')
                self._reload_index = True
        self.reload_index()
                
    def reload_index(self):
        if self._reload_index:
            _logger.info(f'{self.__class__.__name__} starting reload index )')
            try:
                self.make_index()
                self.export_index()
            except Exception as e:
                _logger.error(f'{self.__class__.__name__} error reload index {e})')
                
            
class SampleIDstr:
    """Tools to find the SampleID in a string"""
    
    _std_names = [('David','DW'), ('stephen','SP'), 
                  ('Alish','AS'), ('Aish','AS')]
    
    def __init__(self,string):
        self.SampleID = self.Name_to_SampleID_Name(string)
       
    def Name_to_SampleID_Name(self,string):
        for i,sID in self._std_names:
            if i in string:
                string = string.replace(i,sID)
        return string

 
if __name__ == "__main__":

    try:
        RamanIndex = OrganizeRamanFiles()
#        RamanIndex.index
#        RamanIndex.make_index()
#        RamanIndex.export_index()
    except Exception as e:
        _logger.error(f'Raman Index error: {e}')
