from dataclasses import dataclass, field
from typing import Any
from raman_fitting.config.path_settings import (
    RunModes,
    initialize_run_mode_paths,
    ExportPathSettings,
)
from raman_fitting.config import settings

from raman_fitting.exports.plotting_fit_results import fit_spectrum_plot
from raman_fitting.exports.plotting_raw_data import raw_data_spectra_plot

from loguru import logger

from .models import ExportResultSet


class ExporterError(Exception):
    """Error occurred during the exporting functions"""


@dataclass
class ExportManager:
    run_mode: RunModes
    fit_results: dict[str, Any] = field(default_factory=dict, repr=False)
    export_results: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self.paths = initialize_run_mode_paths(
            self.run_mode, user_package_home=settings.destination_dir
        )

    def export_files(self) -> None:
        exports = []
        if self.fit_results is None:
            raise ExporterError("No fit results to export")

        for group_name, group_results in self.fit_results.items():
            if not group_results:
                logger.debug(f"Group {group_name} does not contain results.")
                continue
            for sample_id, sample_results in group_results.items():
                if not sample_results:
                    logger.debug(
                        f"Group={group_name} and sample={sample_id} does not contain results."
                    )
                    continue

                export_dir = self.paths.results_dir / group_name / sample_id
                export_paths = ExportPathSettings(results_dir=export_dir)

                export_results_set = ExportResultSet()
                try:
                    raw_data_spectra_plot_results = raw_data_spectra_plot(
                        sample_results, export_paths=export_paths
                    )
                    export_results_set += raw_data_spectra_plot_results
                except Exception as exc:
                    logger.error(f"Plotting error, raw_data_spectra_plot: {exc}")

                try:
                    fit_spectrum_plot_results = fit_spectrum_plot(
                        sample_results, export_paths=export_paths
                    )
                    export_results_set += fit_spectrum_plot_results
                except Exception as exc:
                    logger.error(f"Plotting error, fit_spectrum_plot: {exc}")
                    raise exc from exc

                exports.append(
                    {
                        "sample": sample_results,
                        "export_paths": export_paths,
                        "export_results": export_results_set,
                    }
                )
        self.export_results.extend(exports)


def call_export_manager(run_mode: RunModes, results: dict[str, Any]) -> ExportManager:
    """Call the export manager to export the results."""
    export_manager = ExportManager(run_mode, results)
    export_manager.export_files()
    return export_manager
