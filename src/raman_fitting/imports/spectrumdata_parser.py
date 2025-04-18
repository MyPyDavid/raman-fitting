"""
A Pydantic BaseModel for reading and validating spectral data from files.

This class provides a frozen (immutable) model that lazily loads spectral data
when needed and caches it for subsequent access. It includes validation of the
input file path and computed fields for spectrum data, length, and hash.

Attributes:
    filepath (FilePath): Path to the spectrum data file (validated to exist)
    label (str): Label for the spectrum, defaults to "raw"
    region_name (str): Name of the spectral region, defaults to "full"

Computed Fields:
    spectrum (SpectrumData): Lazily loaded and cached spectrum data
    spectrum_length (int): Length of the loaded spectrum
    spectrum_hash (str): SHA256 hash of the spectrum's JSON representation

Example:
    ```python
    reader = SpectrumReader(
        filepath="path/to/spectrum.txt",
        label="sample1",
        region_name="region1"
    )

    # Accessing computed fields (lazy loading)
    spectrum_data = reader.spectrum
    length = reader.spectrum_length
    hash_value = reader.spectrum_hash
    ```

Notes:
    - The model is frozen (immutable) after creation
    - Spectrum data is loaded only when first accessed
    - All computed fields are cached after first access
    - Uses Pydantic V2 for validation and field computation

Created: 2021-07-05
Updated: 2025-04-18
Authors: DW, MyPyDavid
"""

import hashlib
from functools import cached_property
from pydantic import BaseModel, computed_field, FilePath

from raman_fitting.imports.spectrum.parse_spectrum import parse_spectrum_from_file
from raman_fitting.models.spectrum import SpectrumData


class SpectrumReader(BaseModel):
    """
    Reads a spectrum from a 'raw' data file Path or str

    with spectrum_data_keys "ramanshift" and "intensity".
    Double checks the values
    Sets a hash attribute afterwards
    """

    model_config = {
        "frozen": True,  # Makes the model immutable
        "arbitrary_types_allowed": True,  # Needed for SpectrumData
    }

    filepath: FilePath
    label: str = "raw"
    region_name: str = "full"

    @computed_field
    @cached_property
    def spectrum(self) -> SpectrumData:
        """Lazily load and cache the spectrum data"""
        return parse_spectrum_from_file(
            file=self.filepath,
            label=self.label,
            region_name=self.region_name,
        )

    @computed_field
    @cached_property
    def spectrum_length(self) -> int:
        return len(self.spectrum)

    @computed_field
    @cached_property
    def spectrum_hash(self) -> str:
        """Computed hash of the spectrum data"""
        return hashlib.sha256(
            self.spectrum.model_dump_json().encode("utf-8")
        ).hexdigest()
