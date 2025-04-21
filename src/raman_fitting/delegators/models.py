# pylint: disable=W0614,W0401,W0611,W0622,C0103,E0401,E0402
from functools import cached_property
from pathlib import Path
from typing import Dict, Sequence

from pydantic import BaseModel, Field, computed_field

from raman_fitting.imports.files.models import RamanFileInfo
from raman_fitting.imports.samples.models import SampleMetaData

from raman_fitting.models.spectrum import SpectrumData
from raman_fitting.models.fit_models import SpectrumFitModel
from raman_fitting.models.splitter import RegionNames
from raman_fitting.imports.models import SpectrumReader
from raman_fitting.processing.post_processing import SpectrumProcessor


class PreparedSampleSpectrum(BaseModel):
    file_info: RamanFileInfo
    read: SpectrumReader
    processed: SpectrumProcessor

    def __hash__(self):
        # Use the hash of the file path as the hash of the object
        return hash(self.file_info)

    def __eq__(self, other):
        if isinstance(other, PreparedSampleSpectrum):
            return self.file_info == other.file_info
        return False

    @computed_field
    @property
    def sample(self) -> SampleMetaData:
        self.file_info.sample

    @computed_field
    @property
    def source(self) -> Path:
        self.read.filepath


class AggregatedSampleSpectrum(BaseModel):
    """Contains the processed sample spectrum data from several files"""

    prepared_sources: Sequence[PreparedSampleSpectrum]
    spectrum: SpectrumData

    @computed_field
    @cached_property
    def file_info(self) -> set[RamanFileInfo]:
        file_infos = set()
        for source in self.prepared_sources:
            file_infos.add(source.file_info)
        return file_infos

    @computed_field
    @cached_property
    def samples(self) -> set[str]:
        samples = set()
        for source in set(self.prepared_sources):
            samples.add(source.file_info.sample)
        return samples

    @computed_field
    @cached_property
    def sample_id(self) -> str:
        sample_ids = {i.id for i in self.samples}
        if len(sample_ids) > 1:
            raise ValueError("More than one sample id found in sources")
        return sample_ids.pop()


class AggregatedSampleSpectrumFitResult(BaseModel):
    region: RegionNames
    aggregated_spectrum: AggregatedSampleSpectrum = Field(repr=False)
    fit_model_results: Dict[str, SpectrumFitModel]

    def get_fit_model(self, model: str):
        return self.fit_model_results[model]

    def get_fit_model_names(self):
        return self.fit_model_results.keys()

    @computed_field
    @property
    def sources(self) -> list[PreparedSampleSpectrum]:
        return list(set(self.aggregated_spectrum.prepared_sources))

    @computed_field
    @property
    def sample_id(self) -> str:
        return self.aggregated_spectrum.sample_id
