# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402

from pathlib import Path
from itertools import starmap


if __name__ == "__main__":
    from indexer.indexer import MakeRamanFilesIndex
    # from processing.cleaner import SpectrumCleaner
    from processing.spectrum_template import SpectrumTemplate
    from processing.spectrum_constructor import SpectrumDataLoader, SpectrumDataCollection
    from deconvolution_models.fit_models import InitializeModels, Fitter
    from export.exporter import Exporter
    # from config import config

else:
    from ..indexer.indexer import MakeRamanFilesIndex
    # from processing.cleaner import SpectrumCleaner
    from ..processing.spectrum_template import SpectrumTemplate
    from ..processing.spectrum_constructor import SpectrumDataLoader, SpectrumDataCollection
    from ..deconvolution_models.fit_models import InitializeModels, Fitter
    from ..export.exporter import Exporter
    # from ..config import config
    # from raman_fitting.indexer.indexer import OrganizeRamanFiles
    # from raman_fitting.processing.spectrum_constructor import SpectrumDataLoader, SpectrumDataCollection


class MainDelegator():
    # TODO Add flexible input handling for the cli, such a path to dir, or list of files
    #  or create index when no kwargs are given.
    '''
    Main processing loop over an index of Raman files.
    Input parameters is DataFrame of index
    Creates plots and files in the config RESULTS directory.
    '''

    def __init__(self, **kwargs ):
        self._kwargs = kwargs
        self.spectrum = SpectrumTemplate()
        # self.index = RamanIndex
        self.set_default_run_mode()
        self.index_delegator()
        self.run_delegator()

    def set_default_run_mode(self):
        if 'run_mode' not in self._kwargs.keys():
            # TODO maybe give warning or raise Error
            self._kwargs.update({'run_mode' : 'normal'})
            # care default setting
        _run_mode = self._kwargs.get('run_mode', 'normal')
        self.run_mode = _run_mode

    def index_delegator(self):
        _make_rf_index = MakeRamanFilesIndex(**self._kwargs)
        self._make_rf_index = _make_rf_index
        self.index = _make_rf_index.index_selection

    def test_positions(self, sGrp_grp,nm, grp_cols = ['FileStem','SamplePos','FilePath']):
#        grp_cols = ['FileStem','SamplePos','FileCreationDate']
        if sGrp_grp.FileStem.nunique() != sGrp_grp.SamplePos.nunique():
            print(sGrp_grp[grp_cols])
            print(f'Unique files and positions not matching for {nm}')
            return sGrp_grp.groupby(grp_cols),grp_cols
        else:
            return sGrp_grp.groupby(grp_cols),grp_cols

    def add_make_destdirs(self, sample_grp):

        dest_grp_dir = Path(sample_grp.DestDir.unique()[0])  # takes one destination directory from Sample Groups
        dest_fit_plots = dest_grp_dir.joinpath('Fitting_Plots')
        dest_fit_comps = dest_grp_dir.joinpath('Fitting_Components')
        dest_fit_comps.mkdir(parents=True,exist_ok=True)

        dest_raw_data_dir = dest_grp_dir.joinpath('Raw_Data')
        dest_raw_data_dir.mkdir(parents=True,exist_ok=True)

        export_info = {'DestGrpDir' : dest_grp_dir,
                       'DestFittingPlots' : dest_fit_plots,
                       'DestFittingComps' : dest_fit_comps,
                       'DestRaw' : dest_raw_data_dir
                       }
        return export_info 

    def run_delegator(self):
        # TODO remove self.set_models() removed InitModels
        self._failed_samples = []
        self.export_collect = []

        # assert type(self.index) == type(pd.DataFrame())
        if self.run_mode == 'normal':
            if not self.index.empty:
                self._run_gen()
            else:
                pass
                # info raman loop finished because index is empty
        elif 'DEBUG' in self.run_mode:
            try:
                # self._run_gen() # TODO add extra test runs in tests dir
                pass
            except Exception as e:
                print('Error in DEBUG run: ', e)
            # TODO get testing from index and run
            pass
        else:
            pass # warning run mode not understood

    def initialized_models(self):
        return InitializeModels()
    
    def sample_group_gen(self):
        ''' Generator for Sample Groups, yields the name of group and group of the index SampleGroup'''
        for grpnm, sGrp_grp in self.index.groupby(self.spectrum.grp_names.sGrp_cols[0]): # Loop over SampleGroups 
            yield grpnm, sGrp_grp
            
    def _sID_gen(self,grpnm, sGrp_grp):
        ''' Generator for SampleIDs, yields the name of group, name of SampleID and group of the index of the SampleID'''
        for nm, sID_grp in sGrp_grp.groupby(list(self.spectrum.grp_names.sGrp_cols[1:])):# Loop over SampleIDs within SampleGroup
                yield (grpnm, nm, sID_grp)
    
    def _run_gen(self):
        # sort of coordinator coroutine, can implement still deque
        _mygen = self._generator()
        while True:
            try:
                next(_mygen)
            except StopIteration:
                print('StopIteration for mygen')
                break
            finally:
                Exporter(self.export_collect) # clean up and export
        
    def _generator(self):
    
        _sgrpgen = self.sample_group_gen()
        for grpnm, sGrp_grp in _sgrpgen:
            _sID_gen = self._sID_gen(grpnm, sGrp_grp)
            try:
                yield from starmap(self.process_sample_wrapper, _sID_gen)
            
            except GeneratorExit:
                print('Generator closed')
                return

    def coordinator(self):
        pass

    def process_sample_wrapper(self, *args):
        try:
            self.process_sample(*args)
        except Exception as e:
            self._failed_samples.append((e, args))

    def process_sample(self, *args):
        grpnm, nm, sID_grp = args
        sGr, (sID, sDate) = grpnm, nm 
        sGr_out = dict(zip(self.spectrum.grp_names.sGrp_cols, (grpnm,) + nm))
        export_info_out = self.add_make_destdirs(sID_grp)
        sample_pos_grp, sPos_cols = self.test_positions(sID_grp, nm, list(self.spectrum.grp_names.sPos_cols))

        sample_spectra = []
        for meannm, meangrp in sample_pos_grp:  # Loop over individual Sample positions (files) from a SampleID
            sPos_out = dict(zip(self.spectrum.grp_names.sPos_cols,meannm))
            _spectrum_position_info_kwargs = {**sGr_out, **export_info_out, **sPos_out}
            spectrum_data = SpectrumDataLoader(file=meannm[-1], run_kwargs=_spectrum_position_info_kwargs, ovv=meangrp)
            # spectrum_data.plot_raw()
            sample_spectra.append(spectrum_data)

        spectra_collection = SpectrumDataCollection(sample_spectra)
        ft = Fitter(spectra_collection, RamanModels=self.initialized_models())
        rex = Exporter(ft)
        self.export_collect.append(rex)
