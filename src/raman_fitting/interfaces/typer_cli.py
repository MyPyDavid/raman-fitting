from typing import Optional
from typing_extensions import Annotated

from raman_fitting.interfaces.typer_commands.make import make_app
from raman_fitting.interfaces.typer_commands.run import run_app

from .utils import version_callback
from raman_fitting.interfaces.typer_commands.show import show_app

from rich.console import Console
import typer

console = Console()

app = typer.Typer()
state = {"verbose": False}

app.add_typer(run_app, name="run")
app.add_typer(make_app, name="make")
app.add_typer(show_app, name="show")


@app.callback()
def main(
    verbose: bool = False,
    version: Annotated[
        Optional[bool], typer.Option("--version", callback=version_callback)
    ] = None,
):
    """
    Manage raman_fitting in the awesome CLI app.
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


if __name__ == "__main__":
    app()
