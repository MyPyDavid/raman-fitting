from pathlib import Path


from raman_fitting.models.spectrum import SpectrumData

from loguru import logger

from raman_fitting.imports.spectrum.fileparsers.filetypes import (
    SPECTRUM_FILETYPE_PARSERS,
)
from raman_fitting.imports.spectrum.fileparsers.column_headers import (
    get_default_expected_header_keys,
    SpectrumDataKeys,
)
from .validators import (
    SPECTRUM_KEYS_EXPECTED_VALUES,
    validate_values,
)
from ..errors import FileProcessingError, ErrorType


def load_and_parse_spectrum_from_file(
    file: Path | str,
    label: str | None = "raw",
    region_name: str | None = "full",
    header_keys: tuple[SpectrumDataKeys] | None = None,
) -> SpectrumData | FileProcessingError:
    if header_keys is None:
        header_keys = get_default_expected_header_keys()
    if isinstance(file, str):
        # casting str to Path
        file = Path(file)
    file = file.resolve()

    try:
        parser = SPECTRUM_FILETYPE_PARSERS[file.suffix]["method"]
    except KeyError:
        msg = f"No parser found for file type {file.suffix}"
        logger.error(msg)
        return FileProcessingError(file, ErrorType.NOT_IMPLEMENTED, msg)

    spectrum_or_error = parser(file, header_keys=header_keys)
    if isinstance(spectrum_or_error, FileProcessingError):
        return spectrum_or_error

    parsed_spectrum = spectrum_or_error

    spectrum_values_kwargs = {}
    for spectrum_key in parsed_spectrum.headers:
        if spectrum_key not in header_keys:
            # ignore non-header keys?!
            # they must have been excluded already
            continue

        valid, _errors = validate_values(
            parsed_spectrum[spectrum_key], SPECTRUM_KEYS_EXPECTED_VALUES[spectrum_key]
        )
        if valid:
            spectrum_values_kwargs[spectrum_key] = parsed_spectrum[spectrum_key]
        else:
            msg = (
                f"The values of key {spectrum_key} of this spectrum are invalid."
                f"{', '.join(map(str, _errors))}"
            )
            logger.error(msg)
            return FileProcessingError(file, ErrorType.NO_VALID_DATA, msg)

    return SpectrumData(
        label=label,
        region=region_name,
        source=file,
        processing_steps=[f"parsed from:{file.name}. with {parser}"],
        **spectrum_values_kwargs,
    )
