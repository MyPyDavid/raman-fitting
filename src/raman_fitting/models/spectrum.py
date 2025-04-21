import hashlib
from functools import cached_property

import numpy as np

from .deconvolution.spectrum_regions import RegionNames

from pydantic import (
    BaseModel,
    FilePath,
    model_validator,
    Field,
    computed_field,
)
import pydantic_numpy.typing as pnd


class SpectrumData(BaseModel):
    ramanshift: pnd.Np1DArrayFp32 = Field(repr=False, frozen=True)
    intensity: pnd.Np1DArrayFp32 = Field(repr=False, frozen=True)
    label: str = Field(frozen=True)
    source: FilePath | str | set[FilePath] | set[str] = Field(repr=False, frozen=True)
    region: RegionNames = Field(frozen=True)
    processing_steps: list[str] = Field(default_factory=list)

    @computed_field
    @cached_property
    def length(self) -> int:
        return len(self)

    @model_validator(mode="after")
    def validate_equal_length(self):
        if len(self.ramanshift) != len(self.intensity):
            raise ValueError("Spectrum arrays are not of equal length.")
        return self

    @model_validator(mode="after")
    def check_if_contains_nan(self):
        if np.isnan(self.ramanshift).any():
            raise ValueError("Ramanshift contains NaN")

        if np.isnan(self.intensity).any():
            raise ValueError("Intensity contains NaN")
        return self

    def add_processing_step(self, step_name) -> None:
        """Helper method to add a processing step to the spectrum."""
        self.processing_steps.append(step_name)

    @computed_field
    @cached_property
    def spectrum_hash(self) -> str:
        """Computed hash of the spectrum data"""
        return hashlib.sha256(
            (
                "".join(map(str, self.ramanshift)) + "".join(map(str, self.intensity))
            ).encode("utf-8")
        ).hexdigest()

    # length is derived property
    def __len__(self):
        return len(self.ramanshift)
