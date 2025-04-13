import pytest

from raman_fitting.config.path_settings import RunModes
from raman_fitting.delegators.main_delegator import MainDelegator
from raman_fitting.imports.files.selectors import select_samples_from_index


@pytest.fixture(scope="module")
def delegator():
    return MainDelegator(run_mode=RunModes.PYTEST)


@pytest.mark.slow
def test_initialize_models(delegator):
    assert "first_order" in delegator.lmfit_models
    assert "first_order" in delegator.selected_models
    with pytest.raises(KeyError):
        delegator.select_fitting_model("no_name", "no model")


@pytest.mark.slow
def test_delegator_index(delegator):
    assert delegator.index
    assert len(delegator.index.raman_files) == 5
    selection = select_samples_from_index(
        delegator.index.raman_files,
        delegator.select_sample_groups,
        delegator.select_sample_ids,
    )
    assert len(delegator.index.raman_files) == len(selection)


@pytest.mark.slow
def test_main_run(delegator, test_sample_id):
    assert delegator.results
    assert delegator.run_mode_paths.results_dir.exists()
    assert delegator.results["test"][test_sample_id]["first_order"]

    test_results = delegator.results["test"][test_sample_id]
    first_order = test_results["first_order"]
    assert first_order.sample_id == test_sample_id
    for model, spec_fit in first_order.fit_model_results.items():
        assert spec_fit.fit_result.success
        assert spec_fit.elapsed_seconds < 50

    second_order = test_results["second_order"]
    assert second_order.sample_id == test_sample_id
    for model, spec_fit in second_order.fit_model_results.items():
        assert spec_fit.fit_result.success
        assert spec_fit.elapsed_seconds < 50

    for exports in delegator.export_manager.export_results:
        for exp_result in exports["export_results"].results:
            assert exp_result.target.exists()
