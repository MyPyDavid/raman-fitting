""" Indexer for raman data files """
# import sys
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger('pyramdeconv')

import pandas as pd

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

    index_file_sample_cols = ['FileStem','SampleID','SamplePos','SampleGroup', 'FilePath']
    index_file_stat_cols = ['FileCreationDate', 'FileCreation','FileModDate', 'FileMod', 'FileHash']

    debug = False



    def __init__(self, reload_index = True, run_mode = 'normal', costum_datadir = Path(), **kwargs):
        self._cnm = self.__class__.__name__

        self._kwargs = kwargs
        self._reload_index = reload_index
        self._run_mode = run_mode
        self._costum_datadir = costum_datadir

        self.RESULTS_DIR = ''
        self.DATASET_DIR = ''
        self.INDEX_FILE = ''
        self.choose_dirs()

        self.index = pd.DataFrame()
        if not self.debug and not self._reload_index:
            self.index = self.load_index()
        else:
            self.index = self.reload_index()

        self.index_selection = self.index_selection(self.index, self._kwargs)


#        self.ExpOVV = self.ovv(self.ExpFiles)
#        self.ExpDB = FileHelper.FindExpFolder(exp_method).DestDir.joinpath('RAMAN_DB.hdf5')

    def choose_dirs(self):

        if 'DEBUG' in self._run_mode:
            self.debug = True
            RESULTS_DIR = config.TESTS_DIR.parent.joinpath('tests/test_results')
            DATASET_DIR = config.TESTS_DIR.parent.joinpath('tests/test_data')
            INDEX_FILE = RESULTS_DIR.joinpath('test_index.csv')
        else:
            RESULTS_DIR = config.RESULTS_DIR
            DATASET_DIR = config.DATASET_DIR
            INDEX_FILE = config.INDEX_FILE

        if not DATASET_DIR.is_dir() and self._run_mode != 'normal':
            logger.warning(f'This directory does not exist.\n"{DATASET_DIR}"')
            raise FileNotFoundError(f'This directory does not exist:\n{DATASET_DIR}')

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
            logger.warning(f'Error parse_filename for {ramanfilepath} \n{e}')
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

        RF_index_raw = pd.DataFrame(RF_indexed,columns = self.index_file_sample_cols+self.index_file_stat_cols).drop_duplicates(subset=['FileHash'])

        RF_index_raw = RF_index_raw.assign(**{'DestDir' : [self.RESULTS_DIR.joinpath(sGrp) for sGrp in RF_index_raw.SampleGroup.to_numpy()]})
        logger.debug(f'{self._cnm} successfully set index {len(RF_index_raw)} from {len(raman_files_raw)} files')
        return RF_index_raw


    def export_index(self, index):
        if not index.empty:
            index.to_csv(self.INDEX_FILE)
            logger.info(f'{self._cnm} Succesfully Exported Raman Index file to {self.INDEX_FILE}, with len({len(index)})')
        else:
            logger.info(f'{self._cnm} Empty index not exported')

    def load_index(self):

        try:
            index = pd.read_csv(self.INDEX_FILE)
            logger.info(f'Succesfully imported Raman Index file from {self.INDEX_FILE}, with len({len(index)})')
        except Exception as e:
            logger.error(f'Error in load_index from {self.INDEX_FILE},\n{e}\n starting reload index ... ')
            index = self.reload_index()
        return index

    def reload_index(self):
        logger.info(f'{self._cnm} starting reload index )')
        try:
            index = self.make_index()
            self.export_index(index)
        except Exception as e:
            index = pd.DataFrame()
            logger.error(f'{self._cnm} error reload index {e})')
        return index

    def index_selection(self, index=pd.DataFrame(), default_selection: str='', **kwargs):
        '''
        Special selector on the index DataFrame

        Parameters
        -------

        index
            pd.DataFrame containing the index of files
            should contains columns that are given in index_file_sample_cols and index_file_stat_cols
        default_selection str
            all or '' for empty default
        kwargs
            checks for keywords suchs as samplegroups, sampleIDs, extra
            meant for cli commands

        Returns
        -------
        index_selection
            pd.DataFrame with a selection from the given parameter index
            default returns empty DataFrame

        '''
        _kws = kwargs
        _keys = _kws.keys()

        # default_selection = _kws.get('default_selection','')
        index_selection = pd.DataFrame()
        if not index.empty:

            if default_selection:
                if default_selection == 'all':
                    index_selection = index .copy()

            if 'samplegroups' in _keys:
                if _kws['samplegroups']:
                    index_selection = index.loc[index.SampleGroup.str.contains('|'.join(_kws['samplegroups']))]
            if 'sampleIDs' in _keys:
                index_selection = index.loc[index.SampleID.str.contains('|'.join(_kws['sampleIDs']))]

            if 'extra' in _keys:
                runq = _kws.get('run')
                if 'recent' in runq:
                    grp = index.sort_values('FileCreationDate',ascending=False).FileCreationDate.unique()[0]

                    index_selection  =index.loc[index.FileCreationDate == grp]
                    index_selection = index_selection.assign(**{'DestDir' : [Path(i).joinpath(grp.strftime('%Y-%m-%d')) for i in index_selection.DestDir.values]})
        else:
            logger.warning(f'{self._cnm} index selection index arg empty')
        return index_selection

    def __repr__(self):
        return f'{self._cnm} with index ({len(self.index)}'
    def __len__(self):
        return len(self.index)

if __name__ == "__main__":
    try:
        RamanIndex = MakeRamanFilesIndex()
    except Exception as e:
        _logger.error(f'Raman Index error: {e}')
