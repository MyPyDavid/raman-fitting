from raman_fitting.config.path_settings import RunModes, RunModePaths
from raman_fitting.delegators.main_delegator import MainDelegator, main_run
from raman_fitting.delegators.models import AggregatedSampleSpectrumFitResult
from raman_fitting.imports.files.index.models import RamanFileIndex
from raman_fitting.models.deconvolution.spectrum_regions import RegionNames


def make_examples(
    **kwargs,
) -> dict[str, dict[str, dict[RegionNames, AggregatedSampleSpectrumFitResult]]]:
    """Create example instances of MainDelegator for testing."""
    delegator = MainDelegator(
        run_mode=RunModes.PYTEST,
        fit_model_specific_names=["2peaks", "2nd_4peaks"],
        export=False,
        **kwargs,
    )
    assert isinstance(delegator.index, RamanFileIndex)
    assert isinstance(delegator.run_mode_paths, RunModePaths)
    results = main_run(
        delegator.index,
        delegator.select_sample_groups,
        delegator.select_sample_ids,
        delegator.selected_models,
        delegator.use_multiprocessing,
        delegator.fit_model_region_names,
    )
    return results
