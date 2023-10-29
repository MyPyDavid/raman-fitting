# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402
import logging
import sys
from pathlib import Path

import pandas as pd

from raman_fitting.config.filepath_helper import get_directory_paths_for_run_mode
from raman_fitting.deconvolution_models.fit_models import Fitter
from raman_fitting.deconvolution_models.init_models import InitializeModels
from raman_fitting.exporting.exporter import Exporter
from raman_fitting.indexing.indexer import MakeRamanFilesIndex
from raman_fitting.processing.spectrum_constructor import (
    SpectrumDataCollection,
    SpectrumDataLoader,
)
from raman_fitting.utils.exceptions import MainDelegatorError

from raman_fitting.processing.spectrum_template import SpectrumTemplate
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

        self.spectrum = SpectrumTemplate()

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

        # assert type(self.index) == type(pd.DataFrame())
        if self.run_mode in ("normal", "debug", "make_index", "make_examples"):
            RF_indexer = self.index_delegator(
                run_mode=self.run_mode, dataset_dirs=self.dest_dirs, **kwargs
            )
            self.index = RF_indexer.index_selection

            if self.index.empty:
                logger.warning(f"{self._cqnm} index selection empty")

            if self.run_mode == "make_index":
                logger.info(
                    f"{self._cqnm} Debug run mode {self}. Index loaded {RF_indexer}"
                )
                sys.exit(0)

            models = self.initialize_default_models()
            self.kwargs.update({"models": models})
            # IDEA built in a model selection keyword, here or at fitting level and for the cli
            logger.info(
                f"\n{self._cqnm} models initialized for run mode ({self.run_mode}):\n\n{repr(models)}"
            )

            if self.run_mode in ("normal", "make_examples"):
                if not self.index.empty:
                    logger.debug(f"{self._cqnm}. starting run generator.")

                    self._run_gen(**self.kwargs)
                else:
                    pass
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
        else:
            logger.warning(f'Debug run mode "{self.run_mode}" not recognized not in ')
            # warning run mode not recognized

    def initialize_default_models(self):
        try:
            return InitializeModels()
        except Exception as e:
            raise MainDelegatorError(
                "The initialization of models failed. " f" on {self} with excp: {e}"
            )
            return None

    def sample_group_gen(self):
        """Generator for Sample Groups, yields the name of group and group of the index SampleGroup"""
        for grpnm, sGrp_grp in self.index.groupby(
            self.spectrum.grp_names.sGrp_cols[0]
        ):  # Loop over SampleGroups
            yield grpnm, sGrp_grp

    def _sID_gen(self, grpnm, sGrp_grp):
        """Generator for SampleIDs, yields the name of group, name of SampleID and group of the index of the SampleID"""
        for nm, sID_grp in sGrp_grp.groupby(
            list(self.spectrum.grp_names.sGrp_cols[1:])
        ):  # Loop over SampleIDs within SampleGroup
            yield (grpnm, nm, sID_grp)

    def _run_gen(self, **kwargs):
        # #IDEA sort of coordinator coroutine, can implement still deque
        sgrp_grpby = self.index.groupby(self.spectrum.grp_names.sGrp_cols[0])
        logger.info(f"{self._cqnm} _run_gen starting: {kwargs}")
        _mygen = self._generator(sgrp_grpby, **kwargs)
        Exporter(self.export_collect)  # clean up and
        logger.info(
            f"\n{self._cqnm} run finished.\n Results saved in {self.RESULTS_DIR}"
        )

    def _generator(self, sgrp_grpby, **kwargs):
        export_collect = []
        for sgrpnm, sgrp_grp in sgrp_grpby:
            sID_grpby = sgrp_grp.groupby(list(self.spectrum.grp_names.sGrp_cols[1:]))
            logger.info(f"{self._cqnm} _generator starting group: {sgrpnm}")
            exporter_sample = None
            for sIDnm, sIDgrp in sID_grpby:
                try:
                    exporter_sample = self.simple_process_sample_wrapper(
                        sgrpnm, sIDnm, sIDgrp, **kwargs
                    )
                except GeneratorExit:
                    logger.warning(f"{self._cqnm} _generator closed.")
                    return ()
                except Exception as e:
                    logger.warning(f"{self._cqnm} _generator exception: {e}")
                export_collect.append(exporter_sample)
        return export_collect

    def coordinator(self):
        pass

    def simple_process_sample_wrapper(self, *sID_args, **kwargs):
        logger.info(
            f"{self._cqnm} starting simple process_sample_wrapper args:\n\t - {sID_args[0]}\n\t - {kwargs.keys()}"
        )
        exporter_sample = None
        try:
            logger.debug(
                f"{self._cqnm} simple process_sample_wrapper starting:\n\t - {sID_args[1]}"
            )
            exporter_sample = self.process_sample(*sID_args, **kwargs)
            if exporter_sample:
                logger.debug(
                    f"{self._cqnm} simple process_sample_wrapper appending export:\n\t - {exporter_sample}"
                )
                self.export_collect.append(exporter_sample)
        except Exception as e:
            logger.warning(
                f"{self._cqnm} simple process_sample_wrapper exception on call process sample: {e}"
            )
            self._failed_samples.append((e, sID_args, kwargs))
        return exporter_sample

    def test_positions(
        self, sGrp_grp, sIDnm, grp_cols=["FileStem", "SamplePos", "FilePath"]
    ):
        if sGrp_grp.FileStem.nunique() != sGrp_grp.SamplePos.nunique():
            logger.warning(
                f"{sGrp_grp[grp_cols]} Unique files and positions not matching for {sIDnm}"
            )
        return sGrp_grp.groupby(grp_cols), grp_cols

    def process_sample(self, sgrpnm, sIDnm, sID_grp, **kwargs):
        """
        Loops over individual Sample positions (files) from a SampleID and performs the
        fitting, plotting and exporting.
        """
        logger.info(
            f"{self._cqnm} process_sample called:\n\t - {sgrpnm}, {sIDnm}\n\t - {kwargs.keys()}"
        )

        models = kwargs.get("models", None)

        sGr_out = dict(zip(self.spectrum.grp_names.sGrp_cols, (sgrpnm,) + sIDnm))
        export_info_out = add_make_sample_group_destdirs(sID_grp)
        sample_pos_grp, sPos_cols = self.test_positions(
            sID_grp, sIDnm, list(self.spectrum.grp_names.sPos_cols)
        )

        sample_spectra = []
        for meannm, meangrp in sample_pos_grp:
            logger.info(f"{self._cqnm} process sample mean loop file: {meannm}.")
            sPos_out = dict(zip(self.spectrum.grp_names.sPos_cols, meannm))
            _spectrum_position_info_kwargs = {**sGr_out, **export_info_out, **sPos_out}
            spectrum_data = SpectrumDataLoader(
                file=meannm[-1], run_kwargs=_spectrum_position_info_kwargs, ovv=meangrp
            )
            sample_spectra.append(spectrum_data)
        if sample_spectra:
            spectra_collection = SpectrumDataCollection(sample_spectra)
            ft = Fitter(spectra_collection, RamanModels=models)
            rex = Exporter(ft)
            return rex
        else:
            logger.info(
                f"{self._cqnm} process sample spectra empty {','.join(map(str,[sgrpnm, sIDnm]))}."
            )
            return None

    def __repr__(self):
        return f'Maindelegator: run_mode = {self.run_mode}, {", ".join([f"{k} = {str(val)}" for k,val in self.kwargs.items()])}'


def add_make_sample_group_destdirs(sample_grp: pd.DataFrame):
    dest_grp_dir = Path(
        sample_grp.DestDir.unique()[0]
    )  # takes one destination directory from Sample Groups
    dest_fit_plots = dest_grp_dir.joinpath("Fitting_Plots")
    dest_fit_comps = dest_grp_dir.joinpath("Fitting_Components")
    dest_fit_comps.mkdir(parents=True, exist_ok=True)

    dest_raw_data_dir = dest_grp_dir.joinpath("Raw_Data")
    dest_raw_data_dir.mkdir(parents=True, exist_ok=True)

    export_info = {
        "DestGrpDir": dest_grp_dir,
        "DestFittingPlots": dest_fit_plots,
        "DestFittingComps": dest_fit_comps,
        "DestRaw": dest_raw_data_dir,
    }
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
