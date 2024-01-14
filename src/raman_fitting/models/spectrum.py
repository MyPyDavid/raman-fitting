from dataclasses import dataclass
from typing import Tuple
import numpy as np

from pydantic import BaseModel, FilePath, AwareDatetime, model_validator
import pydantic_numpy.typing as pnd


class SpectrumData(BaseModel):
    ramanshift: pnd.Np1DArrayFp32
    intensity: pnd.Np1DArrayFp32
    label: str
    window_name: str = None

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

    # length is derived property
    def __len__(self):
        return len(self.ramanshift)


class SpectrumMetaData(BaseModel):
    sample_id: str
    sample_group: str
    sample_position: str
    creation_date: AwareDatetime
    source_file: FilePath  # FileStem is derived


@dataclass
class NotSpectrumMetaData:
    spec_name: str = "spectrum_info"
    sGrp_cols: Tuple[str] = ("SampleGroup", "SampleID", "FileCreationDate")
    sPos_cols: Tuple[str] = ("FileStem", "SamplePos", "FilePath")
    spectrum_cols: Tuple[str] = ("ramanshift", "intensity_raw", "intensity")
    spectrum_info_cols: Tuple[str] = ("spectrum_length",)
    export_info_cols: Tuple[str] = (
        "DestGrpDir",
        "DestFittingPlots",
        "DestFittingComps",
        "DestRaw",
    )

    @property
    def info_cols(self):
        info_cols = (
            self.sGrp_cols
            + self.sPos_cols
            + self.spectrum_cols
            + self.spectrum_info_cols
            + self.export_info_cols
        )
        return info_cols
