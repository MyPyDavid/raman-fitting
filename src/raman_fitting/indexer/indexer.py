
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
            DestDir = config.TESTS_DIR.parent.joinpath('tests/test_results')
            RamanDataDir = config.TESTS_DIR.parent.joinpath('tests/test_data')
            IndexFile = DestDir.joinpath('test_index.csv')

        else:
            DestDir = config.RESULTS_DIR
            RamanDataDir = config.DATASET_DIR
            IndexFile = config.INDEX_FILE

        if not RamanDataDir.is_dir():
            raise FileNotFoundError(f'This path to directory does not exist.\n {RamanDataDir}')

        if not DestDir.is_dir():
            DestDir.mkdir(exist_ok=True,parents=False)

        self.DestDir = DestDir
        self.RamanDataDir = RamanDataDir
        self.IndexFile = IndexFile
    # def _set_debug_paths(self):

    def find_files(self):
        ''' 
        Creates a list of all raman type files found in the RamanDataDir which are used in the creation of the index.
        '''
        RFs = list(self.RamanDataDir.rglob('*txt'))
        raman_files_raw = [i for i in RFs if not 'fail' in i.stem and not 'Labjournal' in str(i)]
        self.raman_files = raman_files_raw

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
        self.find_files()
        self._error_parse_filenames = []
        RF_indexed = [(self.parse_filename(i)+self.get_file_stats(i)) for i in self.raman_files]
        RF_index_raw = pd.DataFrame(RF_indexed,columns = self.file_sample_cols+self.file_stat_cols).drop_duplicates(subset=['FileHash'])
        RF_index_raw = RF_index_raw.assign(**{'DestDir' : [self.DestDir.joinpath(sGrp) for sGrp in RF_index_raw.SampleGroup.to_numpy()]})
        self.index = RF_index_raw
        _logger.debug(f'{self.__class__.__name__} successfully set index {len(self.index)}')
        
    
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
#        RamanIndex.index
#        RamanIndex.make_index()
#        RamanIndex.export_index()
    except Exception as e:
        _logger.error(f'Raman Index error: {e}')
