from typer.testing import CliRunner
from raman_fitting.interfaces.typer_cli import app

runner = CliRunner()


def test_version_callback():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Awesome Typer CLI Version:" in result.stdout


def test_run_command():
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0


def test_run_command_with_arguments():
    result = runner.invoke(
        app, ["run", "pytest", "--models", "model1", "--sample-ids", "sample1"]
    )
    assert result.exit_code == 1
    assert "No samples were selected" in result.stdout


def test_make_command():
    result = runner.invoke(app, ["make", "--help"])
    assert result.exit_code == 0


def test_make_example_command():
    result = runner.invoke(app, ["make", "example"])
    assert result.exit_code == 0


def test_make_index_command():
    result = runner.invoke(app, ["make", "index"])
    assert result.exit_code == 0
    assert "initialized" in result.stdout
    assert "saved" in result.stdout


def test_make_config_command():
    result = runner.invoke(app, ["make", "config"])
    assert result.exit_code == 0
    assert "Config file created" in result.stdout  # Adjust this based on actual output
