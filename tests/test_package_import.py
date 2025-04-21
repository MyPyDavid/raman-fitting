import pytest


def test_call_version_on_package():
    import raman_fitting

    version = raman_fitting.utils.version()
    assert raman_fitting.__about__.__version__ in version


@pytest.mark.slow
def test_call_make_examples_on_package():
    from raman_fitting.delegators.examples import make_examples
    from lmfit.model import ModelResult

    example_run = make_examples()
    assert example_run
    fit_result = (
        example_run["test"]["testDW38C"]["first_order"]
        .fit_model_results["2peaks"]
        .fit_result
    )
    assert fit_result.success
    assert isinstance(fit_result, ModelResult)


def test_logging_disabled_when_importing_package(caplog):
    # Clear any existing logs
    caplog.clear()

    # Import your package (this should not trigger any logging)
    import raman_fitting
    # Check if no log message is captured in the caplog
    assert caplog.text == ""

    # Emit a log message (this should not be captured)
    raman_fitting.utils.version()

    assert "DEBUG" in caplog.text
