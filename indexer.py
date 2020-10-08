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


if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))
    from FileHelper.FindFolders import FindExpFolder
    from FileHelper.FindSampleID import SampleIDstr,GetSampleID
else:
    sys.path.append(str(Path(__file__).parent.parent))
    from FileHelper.FindFolders import FindExpFolder
    from FileHelper.FindSampleID import SampleIDstr,GetSampleID

__all__= ['OrganizeRamanFiles']

#%%
class OrganizeRamanFiles:   
    """Finds the RAMAN files in the top folder and creates an overview"""
    DestDir = FindExpFolder('RAMAN').DestDir
    def __init__(self):
        self.index = OrganizeRamanFiles.index(self)
#        self.raman_data_files = OrganizeRAMANFiles.find_files()
#        self.ExpFiles = OrganizeRAMANFiles.find_files(FileHelper.FindExpFolder('RAMAN').DataDir)
#        self.ExpOVV = self.ovv(self.ExpFiles)
#        self.ExpDB = FileHelper.FindExpFolder(exp_method).DestDir.joinpath('RAMAN_DB.hdf5')
        
    def index(self):
        files = OrganizeRamanFiles.find_files()
        index = make_index(files)
        return index
        
    @staticmethod
    def find_files(RamanDataDir = FindExpFolder('RAMAN').DataDir):
        RFs = list(RamanDataDir.rglob('*txt'))
        raman_files_raw = [i for i in RFs if not 'fail' in i.stem and not 'Labjournal' in str(i)]
        return raman_files_raw
        
#        RFs_stat = [(i.stat(), hashlib.md5(i.read_text(encoding='utf-8').encode('utf-8')).hexdigest()) for i in RFs_filter]
#        RFs_stat_times = [(pd.to_datetime(i[0].st_ctime,unit='s'), pd.to_datetime(i[0].st_mtime,unit='s'),i[1]) for i in RFs_stat]
#        RF_set_data = [(pd.read_csv(i.FilePath,sep='\t',names=['Frequency',i.FilePath]).set_index('Frequency')) for n,i in RF_set.iterrows()]
#         c = pd.concat([i for i in RF_set_data],axis=1,sort=False)
#        ramanfile_stem = 'MK207_2HT_N2_1'
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
                sID = [SampleIDstr(split[0]).SampleID]
                position = 0
#                split = split + [0]
            elif len(split) >= 3:
                sID = [SampleIDstr('_'.join(split[0:-1])).SampleID]
                position = int(''.join(((filter(str.isdigit,split[-1])))))
#                split =[split_Nr0] + [position]
            elif  len(split) == 0:
                sID = SampleIDstr(split).SampleID
                position = 0
            else:
                 sID = [SampleIDstr(split[0]).SampleID]
                 if ''.join(((filter(str.isdigit,split[-1])))) == '':
                     sID = [ramanfile_stem]
                     position = 0
                 else:
                     position = int(''.join(((filter(str.isdigit,split[-1])))))
            sID = GetSampleID.match_SampleID(sID[0],include_extra=True)
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

def make_index(raman_files_raw = OrganizeRamanFiles.find_files() ):
    file_sample_cols = ['FileStem','SampleID','SamplePos','SampleGroup', 'FilePath']
    file_stat_cols = ['FileCreationDate', 'FileCreation','FileModDate', 'FileMod', 'FileHash']
#    ridx = namedtuple('Raman_index_row', file_sample_cols+file_stat_cols)
    RF_indexed = [(OrganizeRamanFiles.find_SampleID_position(i)+OrganizeRamanFiles.get_file_stats(i)) for i in raman_files_raw]
    RF_index_raw = pd.DataFrame(RF_indexed,columns = file_sample_cols+file_stat_cols).drop_duplicates(subset=['FileHash'])
    
    RamanDestDir = FindExpFolder('RAMAN').DestDir
    RF_index_raw['DestDir'] = RamanDestDir
    
    return RF_index_raw   

 
if __name__ == "__main__":
#    import ..FileHelper
#    files = OrganizeRAMANFiles.find_files()
    RamanIndex = OrganizeRamanFiles().index
    print('Raman indexed')
#    DestDir = FileHelper.FindExpFolder('RAMAN').DestDir