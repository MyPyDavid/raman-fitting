from pathlib import Path

from raman_fitting.models.spectrum import SpectrumData

from loguru import logger

from .datafile_parsers import get_parser_method_for_filetype
from .datafile_schema import get_default_expected_header_keys
from .validators import (
    SPECTRUM_KEYS_EXPECTED_VALUES,
    validate_values,
)


def parse_spectrum_from_file(
    file: Path = None,
    label: str | None = None,
    region_name: str | None = None,
    header_keys: tuple[str] | None = None,
) -> SpectrumData | None:
    parser = get_parser_method_for_filetype(file)
    if header_keys is None:
        header_keys = get_default_expected_header_keys()
    parsed_spectrum = parser(file, header_keys=header_keys)
    if parsed_spectrum is None:
        return None

    spectrum_kwargs = {
        "label": label,
        "region_name": region_name,
        "source": file,
        "processing_steps": [f"parsed from:{file.name}. with {parser}"],
    }
    for spectrum_key in parsed_spectrum.headers:
        if spectrum_key not in header_keys:
            continue

        spectrum_values = parsed_spectrum[spectrum_key]
        valid, _errors = validate_values(
            spectrum_values, SPECTRUM_KEYS_EXPECTED_VALUES[spectrum_key]
        )
        if valid:
            spectrum_kwargs[spectrum_key] = spectrum_values
        else:
            logger.error(
                f"The values of key {spectrum_key} of this spectrum are invalid."
                f"{', '.join(_errors)}"
            )
    return SpectrumData(**spectrum_kwargs)
