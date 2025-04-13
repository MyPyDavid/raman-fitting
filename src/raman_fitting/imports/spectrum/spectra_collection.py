import numpy as np

from pydantic import BaseModel, ValidationError, model_validator, Field, computed_field

from raman_fitting.models.deconvolution.spectrum_regions import RegionNames
from raman_fitting.models.spectrum import SpectrumData


def aggregate_mean_spectrum_from_spectra(spectra: list[SpectrumData]) -> SpectrumData:
    # wrap this in a ProcessedSpectraCollection model
    mean_int = np.mean(np.vstack([i.intensity for i in spectra]), axis=0)
    mean_ramanshift = np.mean(np.vstack([i.ramanshift for i in spectra]), axis=0)

    region_name = list(set(i.region_name for i in spectra))
    if len(region_name) > 1:
        raise ValueError(
            f"The spectra have different region names where they should be the same.\n\t{region_name}"
        )
    region_name = region_name[0]

    # check that all spectra have the same processing steps
    new_processing_steps = []
    for spec in spectra:
        for i in spec.processing_steps:
            if i not in new_processing_steps:
                new_processing_steps.append(i)
    new_processing_steps.append(
        f"aggregated {region_name} with np.mean of {len(spectra)} spectra"
    )

    mean_spec = SpectrumData(
        ramanshift=mean_ramanshift,
        intensity=mean_int,
        label=f"clean_{region_name}_mean",
        region_name=region_name,
        source=[i.source for i in spectra],
        processing_steps=new_processing_steps,
    )
    return mean_spec


class SpectraDataCollection(BaseModel):
    spectra: list[SpectrumData] = Field(min_length=1, repr=False)
    region_name: RegionNames
    # mean_spectrum: SpectrumData = Field(init=False)

    @model_validator(mode="after")
    def check_spectra_have_same_label(self) -> "SpectraDataCollection":
        """checks member of lists"""
        labels = set(i.label for i in self.spectra)
        if len(labels) > 1:
            raise ValidationError(f"Spectra have different labels {labels}")
        return self

    @model_validator(mode="after")
    def check_spectra_have_same_region(self) -> "SpectraDataCollection":
        """checks member of lists"""
        region_names = set(i.region_name for i in self.spectra)
        if len(region_names) > 1:
            raise ValidationError(f"Spectra have different region_names {region_names}")
        return self

    @model_validator(mode="after")
    def check_spectra_lengths(self) -> "SpectraDataCollection":
        unique_lengths_rs = set(len(i.ramanshift) for i in self.spectra)
        unique_lengths_int = set(len(i.intensity) for i in self.spectra)
        if len(unique_lengths_rs) > 1:
            raise ValidationError(
                f"The spectra have different ramanshift lengths where they should be the same.\n\t{unique_lengths_rs}"
            )
        if len(unique_lengths_int) > 1:
            raise ValidationError(
                f"The spectra have different intensity lengths where they should be the same.\n\t{unique_lengths_int}"
            )

        return self

    @computed_field
    @property
    def mean_spectrum(self) -> SpectrumData:
        return aggregate_mean_spectrum_from_spectra(self.spectra)
