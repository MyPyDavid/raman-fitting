""" Indexer for raman data files """
import hashlib
import logging
import sys
from pathlib import Path

import pandas as pd

from .. import __package_name__

# parse_filepath_to_sid_and_pos
from ..config import config, filepaths
from .filename_parser import PathParser

# get_directory_paths_for_run_mode
# from .index_selection import index_selection

logger = logging.getLogger(__package_name__)

__all__ = ["MakeRamanFilesIndex"]

#%%


class MakeRamanFilesIndex:
    """

    Finds the RAMAN files in the data folder from config and creates an overview, on the attribute .index
    finds a list of files,

    """

    # index_file_sample_cols = {'FileStem': 'string',
    #                           'SampleID': 'string',
    #                           'SamplePos': 'int64',
    #                           'SampleGroup': 'string',
    #                           'FilePath': 'string')
    # index_file_stat_cols = ('FileCreationDate' , 'FileCreation','FileModDate', 'FileMod', 'FileHash')
    # INDEX_FILE_NAME = 'index.csv'
    debug = False

    # RESULTS_DIR = config.RESULTS_DIR,
    #              DATASET_DIR = config.DATASET_DIR,
    #              INDEX_FILE = config.INDEX_FILE,
    def __init__(
        self, force_reload=True, run_mode="normal", extra_dataset_dirs=[], **kwargs
    ):

        self._cqnm = self.__class__.__qualname__

        self._kwargs = kwargs
        self.force_reload = force_reload
        self.run_mode = run_mode
        self._extra_dataset_dirs = extra_dataset_dirs

        self._dest_dirs = filepaths.get_directory_paths_for_run_mode(run_mode, **kwargs)
        for k, val in self._dest_dirs.items():
            setattr(self, k, val)

        # self.get_index_file_path(dest_dir = self.RESULTS_DIR)
        self.raman_files = self.find_files(data_dir=self.DATASET_DIR)
        # self.choose_dirs()
        self.index = pd.DataFrame()
        self._error_parse_filenames = []
        if "normal" in run_mode and not self.debug and not self.force_reload:
            self.index = self.load_index()

        else:
            self.index = self.reload_index()

        self.index_selection = self.index_selection(self.index, **self._kwargs)

    #        self.ExpOVV = self.ovv(self.ExpFiles)
    #        self.ExpDB = FileHelper.FindExpFolder(exp_method).DestDir.joinpath('RAMAN_DB.hdf5')

    def find_files(self, data_dir=Path()):
        """
        Creates a list of all raman type files found in the DATASET_DIR which are used in the creation of the index.
        """
        raman_files_raw = []
        if data_dir.exists():
            RFs = data_dir.rglob("*txt")
            if RFs:
                raman_files_raw = [
                    i
                    for i in RFs
                    if not "fail" in i.stem and not "Labjournal" in str(i)
                ]
                logger.info(
                    f"{self._cqnm} {len(raman_files_raw)} files were found in the chosen data dir:\n\t{data_dir}"
                )
            else:
                logger.warning(
                    f"{self._cqnm} the chose data file dir was empty.\n{data_dir}\mPlease choose another directory which contains your data files."
                )
        else:
            logger.warning(
                f"{self._cqnm} the chosen data file dir does not exists.\n{data_dir}\nPlease choose an existing directory which contains your data files."
            )

        return raman_files_raw

    # def parse_filename(self,ramanfilepath):
    #     ''' parses a filename into relevant parts for indexer. SampleID, SamplePosition and SampleGroup.'''
    #     try:
    #         _res = parse_filepath_to_sid_and_pos(ramanfilepath)
    #     except Exception as e:
    #         logger.warning(f'Error parse_filename for {ramanfilepath} \n{e}')
    #         _res = ()
    #         self._error_parse_filenames.append((ramanfilepath,e))
    #     return _res

    # @staticmethod
    # def get_file_stats(ramanfilepath, col_names = ()):
    #     ''' get status metadata from a file'''
    #     fstat = ramanfilepath.stat()
    #     ct, mt = pd.to_datetime(fstat.st_ctime,unit='s'), pd.to_datetime(fstat.st_mtime,unit='s')
    #     ct_date, mt_date = ct.date(),mt.date()
    #     filehash = hashlib.md5(ramanfilepath.read_text(encoding='utf-8').encode('utf-8')).hexdigest()
    #     filestat_out = ct_date, ct, mt_date, mt, filehash
    #     if len(col_names) == len(filestat_out):
    #         filestat_out =  dict(zip(col_names, filestat_out))
    #     return filestat_out

    def make_index(self):
        """loops over the files and scrapes the index data from each file"""
        #    ridx = namedtuple('Raman_index_row', file_sample_cols+file_stat_cols)
        raman_files = self.raman_files
        # breakpoint()
        # self.find_files(data_dir=self.DATASET_DIR)
        pp_collection = []
        for file in raman_files:
            try:
                pp_res = PathParser(Path(file))
                pp_collection.append(pp_res)
            except Exception as e:
                logger.warning(
                    f"{self._cqnm} unexpected error for calling PathParser on\n{file}.\n{e}"
                )
                self._error_parse_filenames.append([file, e])
            # _fname = self.parse_filename(file)
            # _fstat = self.get_file_stats(file)
        # RF_indexed = [(self.parse_filename(i)+self.get_file_stats(i)) for i in raman_files ]

        index = pd.DataFrame([i.parse_result for i in pp_collection])
        index = self._extra_assign_destdir_and_set_paths(index)
        # pd.DataFrame(RF_index,columns = self.index_file_sample_cols+self.index_file_stat_cols).drop_duplicates(subset=['FileHash'])
        logger.info(
            f"{self._cqnm} successfully made index {len(index)} from {len(raman_files)} files"
        )
        if self._error_parse_filenames:
            logger.info(
                f"{self._cqnm} errors for filename parser {len(self._error_parse_filenames)} from {len(raman_files)} files"
            )
        return index

    def _extra_assign_destdir_and_set_paths(self, index: pd.DataFrame):
        """assign the DestDir column to index and sets column values as object type"""

        if hasattr(index, "SampleGroup"):
            index = index.assign(
                **{
                    "DestDir": [
                        self.RESULTS_DIR.joinpath(sGrp)
                        for sGrp in index.SampleGroup.to_numpy()
                    ]
                }
            )
        _path_dtypes_map = {
            k: val for k, val in PathParser.index_dtypes.items() if "Path" in val
        }
        for k, val in _path_dtypes_map.items():
            if hasattr(index, k):
                if "Path" in val:
                    index[k] = [Path(i) for i in index[k].to_numpy()]
        return index

    def export_index(self, index):
        """saves the index to a defined Index file"""
        if not index.empty:
            if not self.INDEX_FILE.parent.exists():
                logger.info(
                    f"{self._cqnm} created parent dir: {self.INDEX_FILE.parent}"
                )
                self.INDEX_FILE.parent.mkdir(exist_ok=True, parents=True)

            index.to_csv(self.INDEX_FILE)

            _dtypes = index.dtypes.to_frame("dtypes")
            _dtypes.to_csv(self._dtypes_filepath())

            logger.info(
                f"{self._cqnm} Succesfully Exported Raman Index file to:\n\t{self.INDEX_FILE}\nwith len({len(index)})."
            )
        else:
            logger.info(f"{self._cqnm} Empty index not exported")

    def load_index(self):
        """loads the index from from defined Index file"""
        if self.INDEX_FILE.exists():
            try:

                _dtypes = pd.read_csv(self._dtypes_filepath(), index_col=[0]).to_dict()[
                    "dtypes"
                ]

                _dtypes_datetime = {
                    k: val
                    for k, val in _dtypes.items()
                    if "datetime" in val or k.endswith("Date")
                }

                _dtypes_no_datetime = {
                    k: val
                    for k, val in _dtypes.items()
                    if k not in _dtypes_datetime.keys()
                }

                index = pd.read_csv(
                    self.INDEX_FILE,
                    index_col=[0],
                    dtype=_dtypes_no_datetime,
                    parse_dates=list(_dtypes_datetime.keys()),
                )
                index = self._extra_assign_destdir_and_set_paths(index)

                logger.info(
                    f"Succesfully imported Raman Index file from {self.INDEX_FILE}, with len({len(index)})"
                )
                if not len(self.index) == (
                    len(self.raman_files) + len(self._error_parse_filenames)
                ):
                    logger.error(
                        f"""'Error in load_index from {self.INDEX_FILE},
                                 \nlength of loaded index not same as number of raman files
                                 \n starting reload index ... """
                    )
                    self.index = self.reload_index()

            except Exception as e:
                logger.error(
                    f"Error in load_index from {self.INDEX_FILE},\n{e}\n starting reload index ... "
                )
                index = self.reload_index()
        else:
            logger.error(
                f"Error in load_index: {self.INDEX_FILE} does not exists, starting reload index ... "
            )
            index = self.reload_index()
        return index

    def reload_index(self):
        """restarts the index creation from scratch and export."""
        logger.info(f"{self._cqnm} starting reload index.")
        index = pd.DataFrame()

        try:
            logger.info(f"{self._cqnm} making index.")

            try:
                index = self.make_index()
            except Exception as e:
                logger.error(f"{self._cqnm} make index error:\n\t{e}")

            try:
                self.export_index(index)
            except Exception as e:
                logger.error(f"{self._cqnm} export after make index error:\n\t{e}")

        except Exception as e:
            logger.error(f"{self._cqnm} reload index error:\n\t{e}")

        return index

    def index_selection(
        self, index=pd.DataFrame(), default_selection: str = "", **kwargs
    ):
        """
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
            pd.DataFrame with a selection from the given input parameter index
            default returns empty DataFrame

        """

        _kws = kwargs
        _keys = _kws.keys()

        default_selection = _kws.get("default_selection", default_selection)
        if not "normal" in _kws.get("run_mode", default_selection):
            default_selection = "all"
        index_selection = pd.DataFrame()
        logger.info(
            f"{self._cqnm} starting index selection from index({len(index)}) with:\n default selection: {default_selection}\n and {kwargs}"
        )

        if not index.empty:

            if default_selection:
                if default_selection == "all":
                    index_selection = index.copy()

            if "samplegroups" in _keys:
                if _kws["samplegroups"]:
                    index_selection = index.loc[
                        index.SampleGroup.str.contains("|".join(_kws["samplegroups"]))
                    ]
            if "sampleIDs" in _keys:
                index_selection = index.loc[
                    index.SampleID.str.contains("|".join(_kws["sampleIDs"]))
                ]

            if "extra" in _keys:
                runq = _kws.get("run")
                if "recent" in runq:
                    grp = index.sort_values(
                        "FileCreationDate", ascending=False
                    ).FileCreationDate.unique()[0]

                    index_selection = index.loc[index.FileCreationDate == grp]
                    index_selection = index_selection.assign(
                        **{
                            "DestDir": [
                                Path(i).joinpath(grp.strftime("%Y-%m-%d"))
                                for i in index_selection.DestDir.values
                            ]
                        }
                    )
            logger.info(
                f"{self._cqnm} finished index selection from index({len(index)}) with:\n {default_selection}\n and {kwargs}\n selection len({len(index_selection )})"
            )
        else:
            logger.warning(f"{self._cqnm} index selection index arg empty")

        if index_selection.empty:
            logger.warning(f"{self._cqnm} index selection empty. exiting")
            sys.exit()

        return index_selection

    def _dtypes_filepath(self):
        _dtypes_filepath = self.INDEX_FILE.with_name(
            self.INDEX_FILE.stem + "_dtypes" + self.INDEX_FILE.suffix
        )
        return _dtypes_filepath

    def __repr__(self):
        return f"{self._cqnm} with index ({len(self.index)})"

    def __len__(self):
        return len(self.index)


if __name__ == "__main__":
    try:
        RamanIndex = MakeRamanFilesIndex(run_mode="make_examples")
    except Exception as e:
        logger.error(f"Raman Index error: {e}")
