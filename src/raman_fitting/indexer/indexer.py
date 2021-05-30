
# import sys
import hashlib
import logging
# import typing as t

from pathlib import Path
# from collections import namedtuple

import pandas as pd


_logger = logging.getLogger(__name__)

from .filename_parser import parse_filepath_to_sid_and_pos
from ..config import config
# from .index_selection import index_selection

__all__= ['MakeRamanFilesIndex']

#%%


class MakeRamanFilesIndex:   
    """
    
    Finds the RAMAN files in the data folder from config and creates an overview, on the attribute .index
    finds a list of files, 
    
    """
    
    file_sample_cols = ['FileStem','SampleID','SamplePos','SampleGroup', 'FilePath']
    file_stat_cols = ['FileCreationDate', 'FileCreation','FileModDate', 'FileMod', 'FileHash']


    def __init__(self, reload_index = True, run_mode = 'normal', costum_datadir = Path(), **kwargs):
        self._kwargs = kwargs
        self._reload_index = reload_index
        self._run_mode = run_mode
        self.index = pd.DataFrame()
        self.choose_dirs()
        self.load_index()
        self.index_selection = pd.DataFrame()
        self.set_index_selection()

#        self.ExpOVV = self.ovv(self.ExpFiles)
#        self.ExpDB = FileHelper.FindExpFolder(exp_method).DestDir.joinpath('RAMAN_DB.hdf5')

    def choose_dirs(self):

        if 'DEBUG' in self._run_mode:
            RESULTS_DIR = config.TESTS_DIR.parent.joinpath('tests/test_results')
            DATASET_DIR = config.TESTS_DIR.parent.joinpath('tests/test_data')
            INDEX_FILE = RESULTS_DIR.joinpath('test_index.csv')

        else:
            RESULTS_DIR = config.RESULTS_DIR
            DATASET_DIR = config.DATASET_DIR
            INDEX_FILE = config.INDEX_FILE

        if not DATASET_DIR.is_dir() and self._run_mode != 'normal':
            raise FileNotFoundError(f'The path to this directory does not exist.\n"{DATASET_DIR}"')

        if not RESULTS_DIR.is_dir():
            RESULTS_DIR.mkdir(exist_ok=True,parents=True)

        self.RESULTS_DIR = RESULTS_DIR
        self.DATASET_DIR = DATASET_DIR
        self.INDEX_FILE = INDEX_FILE
    # def _set_debug_paths(self):

    def find_files(self):
        ''' 
        Creates a list of all raman type files found in the DATASET_DIR which are used in the creation of the index.
        '''
        RFs = self.DATASET_DIR.rglob('*txt')
        raman_files_raw = [i for i in RFs if not 'fail' in i.stem and not 'Labjournal' in str(i)]
        return raman_files_raw

    def parse_filename(self,ramanfilepath):
        try:
            _res = parse_filepath_to_sid_and_pos(ramanfilepath)
        except Exception as e:
            _logger(f'Error parse_filename for {ramanfilepath} \n{e}')
            _res = ()
            self._error_parse_filenames.append((ramanfilepath,e))
        return _res

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
        raman_files_raw = self.find_files()
        self._error_parse_filenames = []
        RF_indexed = [(self.parse_filename(i)+self.get_file_stats(i)) for i in raman_files_raw]
        RF_index_raw = pd.DataFrame(RF_indexed,columns = self.file_sample_cols+self.file_stat_cols).drop_duplicates(subset=['FileHash'])
        RF_index_raw = RF_index_raw.assign(**{'DestDir' : [self.RESULTS_DIR.joinpath(sGrp) for sGrp in RF_index_raw.SampleGroup.to_numpy()]})
        self.index = RF_index_raw
        _logger.debug(f'{self.__class__.__name__} successfully set index {len(self.index)}')
        
    
    def export_index(self):
        if not self.index.empty:
            self.index.to_csv(self.INDEX_FILE)
            _logger.info(f'Succesfully Exported Raman Index file to {self.INDEX_FILE}, with len({len(self.index)})')
    
    def load_index(self):
        if not self._reload_index:
            try:
                _index_load = pd.read_csv(self.INDEX_FILE)
                _logger.info(f'Succesfully imported Raman Index file from {self.INDEX_FILE}, with len({len(_index_load)})')
                self.index = _index_load
            except:
                _logger.error(f'Error in load_index from {self.INDEX_FILE}, restarting make_index ... )')
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

    def set_index_selection(self, default_selection=''):
        '''
        Special selector on the index DataFrame
        
        Parameters
        -------
        default_selection str
            all or '' for empty default
        self._kwargs
            checks for keywords suchs as samplegroups, sampleIDs, extra
            meant for cli commands

        Returns
        -------
        sets attribute index_selection

        '''
        _kws = self._kwargs
        _keys = _kws.keys()
        RamanIndex_all = self.index
        # default_selection = _kws.get('default_selection','')
        index_selection = pd.DataFrame()
        if default_selection:
            if default_selection == 'all':
                index_selection = RamanIndex_all .copy()
            
            pd.DataFrame()
        if 'samplegroups' in _keys:
            if _kws['samplegroups']:
                index_selection = RamanIndex_all.loc[RamanIndex_all.SampleGroup.str.contains('|'.join(_kws['samplegroups']))]
        if 'sampleIDs' in _keys:
            index_selection = RamanIndex_all.loc[RamanIndex_all.SampleID.str.contains('|'.join(_kws['sampleIDs']))]

        if 'extra' in _keys:
            runq = _kws.get('run')
            if 'recent' in runq:
                grp = RamanIndex_all.sort_values('FileCreationDate',ascending=False).FileCreationDate.unique()[0]

                index_selection  =RamanIndex_all.loc[RamanIndex_all.FileCreationDate == grp]
                index_selection = index_selection.assign(**{'DestDir' : [Path(i).joinpath(grp.strftime('%Y-%m-%d')) for i in index_selection.DestDir.values]})
        self.index_selection = index_selection 

if __name__ == "__main__":

    try:
        RamanIndex = MakeRamanFilesIndex()
    except Exception as e:
        _logger.error(f'Raman Index error: {e}')
