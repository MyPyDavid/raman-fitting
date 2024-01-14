# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402
import logging
import sys

from itertools import groupby


from raman_fitting.config.filepath_helper import get_directory_paths_for_run_mode

from raman_fitting.models.deconvolution.init_models import InitializeModels
from raman_fitting.exports.exporter import Exporter
from raman_fitting.imports.files.file_indexer import MakeRamanFilesIndex
from raman_fitting.imports.spectrum.spectrum_constructor import SpectrumDataLoader
from raman_fitting.imports.spectrum.spectra_collection import SpectraDataCollection

from raman_fitting.utils.exceptions import MainDelegatorError

from raman_fitting.models.spectrum import NotSpectrumMetaData
from raman_fitting.interfaces.cli import RUN_MODES

if __name__ == "__main__":
    pass

logger = logging.getLogger(__name__)


class MainDelegator:
    # IDEA Add flexible input handling for the cli, such a path to dir, or list of files
    #  or create index when no kwargs are given.
    """
    Main delegator for the processing of files containing Raman spectra.

    Input parameters is DataFrame of index
    Creates plots and files in the config RESULTS directory.
    """

    def __init__(self, run_mode="normal", **kwargs):
        self.kwargs = kwargs
        self._cqnm = __class__.__qualname__

        self.run_mode = run_mode
        if run_mode not in RUN_MODES:
            logger.warning(
                f"{self}\n\twarning run_mode choice {run_mode} not in\n\t{RUN_MODES}"
            )

        self.dest_dirs = get_directory_paths_for_run_mode(run_mode=run_mode)
        self.RESULTS_DIR = self.dest_dirs["RESULTS_DIR"]
        self.DATASET_DIR = self.dest_dirs["DATASET_DIR"]
        self.INDEX_FILE = self.dest_dirs["INDEX_FILE"]

        self.spectrum = NotSpectrumMetaData()
        self.models = InitializeModels()

        self.run_delegator(**self.kwargs)

    def index_delegator(self, **kwargs):
        RF_index = MakeRamanFilesIndex(
            **kwargs,
        )
        logger.info(f"index_delegator index prepared with len {len(RF_index)}")
        return RF_index

    def run_delegator(self, **kwargs):
        # IDEA remove self.set_models() removed InitModels
        self._failed_samples = []
        self.export_collect = []

        if self.run_mode not in ("normal", "debug", "make_index", "make_examples"):
            logger.warning(f'Debug run mode "{self.run_mode}" not recognized not in ')
            # warning run mode not recognized
            return
        RF_indexer = self.index_delegator(
            run_mode=self.run_mode, dataset_dirs=self.dest_dirs, **kwargs
        )
        self.index = RF_indexer.index_selection
        if self.index is None:
            logger.warning(f"{self._cqnm} index selection is None")
        elif not self.index:
            logger.warning(f"{self._cqnm} index selection empty")

        if self.run_mode == "make_index":
            logger.info(
                f"{self._cqnm} Debug run mode {self}. Index loaded {RF_indexer}"
            )
            sys.exit(0)

        models = self.models

        self.kwargs.update({"models": models})
        # IDEA built in a model selection keyword, here or at fitting level and for the cli
        logger.info(
            f"\n{self._cqnm} models initialized for run mode ({self.run_mode}):\n\n{repr(models)}"
        )

        if self.run_mode in ("normal", "make_examples"):
            if self.index is None:
                return
            elif self.index:
                logger.debug(f"{self._cqnm}. starting run generator.")

                self._run_gen(**self.kwargs)

            # info raman loop finished because index is empty
        elif self.run_mode == "debug":
            logger.debug(f"Debug run mode {self}. Models initialized {models}")

            try:
                # self._run_gen() # IDEA add extra test runs in tests dir
                pass
            except Exception as e:
                raise MainDelegatorError(
                    "The debug run failed. " f" on {self} because {e}"
                )
            # raise('Error in DEBUG run: ', e)
        else:
            logger.warning(f"Debug run mode {self.run_mode} not recognized")
        # IDEA get testing from index and run

    @staticmethod
    def sample_group_gen(index):
        """Generator for Sample Groups, yields the name of group and group of the index SampleGroup"""
        grouper = groupby(index, key=lambda x: x.sample.group)
        return grouper

    @staticmethod
    def sample_id_gen(group_files):
        """Generator for SampleIDs, yields the name of group, name of SampleID and group of the index of the SampleID"""
        grouper = groupby(group_files, key=lambda x: x.sample.id)
        return grouper

    def _run_gen(self, **kwargs):
        # #IDEA sort of coordinator coroutine, can implement still deque
        logger.info(f"{self._cqnm} _run_gen starting: {kwargs}")
        _mygen = self._generator(**kwargs)
        Exporter(self.export_collect)  # clean up and
        logger.info(
            f"\n{self._cqnm} run finished.\n Results saved in {self.RESULTS_DIR}"
        )

    def _generator(self, **kwargs):
        # breakpoint()
        sample_group_groupby = self.sample_group_gen(self.index)
        export_collect = []
        for sample_group_name, group_files in sample_group_groupby:
            sample_id_grouper = self.sample_id_gen(group_files)

            logger.info(f"{self._cqnm} _generator starting group: {sample_group_name}")
            exporter_sample = None
            for sample_id, sample_group_files in sample_id_grouper:
                try:
                    sample_group_files = list(sample_group_files)
                    exporter_sample = self.simple_process_sample_wrapper(
                        sample_group_name, sample_id, sample_group_files, **kwargs
                    )
                except GeneratorExit:
                    logger.warning(f"{self._cqnm} _generator closed.")
                    return ()
                except Exception as exc:
                    logger.warning(f"{self._cqnm} _generator exception: {exc}")
                export_collect.append(exporter_sample)
        return export_collect

    def simple_process_sample_wrapper(
        self, sample_group_name, sample_id, sample_group_files, **kwargs
    ):
        logger.info(
            f"{self._cqnm} starting simple process_sample_wrapper args:\n\t - {sample_group_name}\n\t - {kwargs.keys()}"
        )
        exporter_sample = None
        # breakpoint()
        try:
            logger.debug(
                f"{self._cqnm} simple process_sample_wrapper starting:\n\t - {sample_id}"
            )
            exporter_sample = self.process_sample(
                sample_group_name, sample_id, sample_group_files, **kwargs
            )
            if exporter_sample:
                logger.debug(
                    f"{self._cqnm} simple process_sample_wrapper appending export:\n\t - {exporter_sample}"
                )
                self.export_collect.append(exporter_sample)
        except Exception as e:
            logger.warning(
                f"{self._cqnm} simple process_sample_wrapper exception on call process sample: {e}"
            )
            self._failed_samples.append(
                (e, sample_group_name, sample_id, sample_group_files, kwargs)
            )
        return exporter_sample

    @staticmethod
    def test_positions(sample_group_files):
        if not sample_group_files:
            return

        _files = [i.file for i in sample_group_files]
        _positions = [i.sample.position for i in sample_group_files]
        if len(set(_files)) != len(set(_positions)):
            logger.warning(
                f"{sample_group_files[0].sample} Unique files and positions not matching for {sample_group_files}"
            )
        return sample_group_files

    def process_sample(
        self, sample_group_name, sample_id, sample_group_files, **kwargs
    ):
        """
        Loops over individual Sample positions (files) from a SampleID and performs the
        fitting, plotting and exporting.
        """
        logger.info(
            f"{self._cqnm} process_sample called:\n\t - {sample_group_name}, {sample_id}\n\t - {kwargs.keys()}"
        )
        # breakpoint()
        # sGr_out = dict(zip(self.spectrum.sGrp_cols, (sample_group_name,) + sample_id))
        # export_info_out = add_make_sample_group_destdirs(sample_group_files)
        sample_group_files = self.test_positions(sample_group_files)

        sample_spectra = []
        for raman_file in sample_group_files:
            logger.info(
                f"{self._cqnm} process sample mean loop file: {raman_file.file.stem}."
            )
            # sPos_out = dict(zip(self.spectrum.sPos_cols, sample_id))
            # _spectrum_position_info_kwargs = {**sGr_out, **export_info_out, **sPos_out}
            spectrum_data = SpectrumDataLoader(file=raman_file.file)
            sample_spectra.append(spectrum_data)
        if not sample_spectra:
            logger.info(
                f"{self._cqnm} process sample spectra empty {','.join(map(str,[sample_group_name, sample_id]))}."
            )
        breakpoint()
        spectra_collection = SpectraDataCollection(**{"spectra": sample_spectra})
        # ft = Fitter(spectra_collection, RamanModels=models)
        rex = Exporter(spectra_collection)
        return rex

    def __repr__(self):
        return f'Maindelegator: run_mode = {self.run_mode}, {", ".join([f"{k} = {str(val)}" for k,val in self.kwargs.items()])}'


def add_make_sample_group_destdirs(sample_grp):
    export_info = sample_grp
    return export_info


def process_sample_wrapper(fn, *args, **kwargs):
    def wrapper(*args, **kwargs):
        logger.debug(
            f"process_sample_wrapper args:\n\t - {fn}\n\t - {args}\n\t - {kwargs.keys()}"
        )
        exp_sample = None
        try:
            exp_sample = fn(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"process_sample_wrapper process_sample_wrapper exception on call {fn}: {e}"
            )
            exp_sample = (e, args, kwargs)

        return exp_sample


def make_examples():
    _main_run = MainDelegator(run_mode="make_examples")
    return _main_run
