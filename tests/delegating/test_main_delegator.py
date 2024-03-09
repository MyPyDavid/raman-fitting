
import pytest

from raman_fitting.config.path_settings import RunModes
from raman_fitting.delegating.main_delegator import MainDelegator


@pytest.fixture(scope='module')
def delegator():
    return MainDelegator(run_mode=RunModes.PYTEST)

def test_initialize_models(delegator):
    
    assert "first_order" in delegator.lmfit_models
    assert "first_order" in delegator.selected_models
    with pytest.raises(KeyError):
        delegator.select_fitting_model("no_name","no model")

def test_index(delegator):
    # breakpoint()
    # index = delegator.select_samples_from_index()
    assert delegator.index
    assert len(delegator.index.raman_files) == 5
    selection = delegator.select_samples_from_index()
    assert len(delegator.index.raman_files) == len(selection)

@pytest.mark.skip(reason="enable main_run before release.")
def test_main_run():
    delegator.main_run()
    assert delegator.results
