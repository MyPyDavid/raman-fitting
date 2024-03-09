import logging
from operator import itemgetter
from typing import Dict, List

import numpy as np

from pydantic import BaseModel, ValidationError, model_validator, ConfigDict

from .spectrum_constructor import SpectrumDataLoader
from raman_fitting.models.spectrum import SpectrumData

logger = logging.getLogger(__name__)
SPECTRUM_KEYS = ("ramanshift", "intensity")


class PostProcessedSpectrum(BaseModel):
    pass


class SpectraDataCollection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    spectra: List[SpectrumDataLoader]

    @model_validator(mode="after")
    def check_spectra_have_clean_spectrum(self) -> "SpectraDataCollection":
        """checks member of lists"""
        if not all(hasattr(spec, "clean_spectrum") for spec in self.spectra):
            raise ValidationError("missing clean_data attribute")
        return self

    @model_validator(mode="after")
    def check_spectra_lengths(self) -> "SpectraDataCollection":
        unique_lengths = set([i.spectrum_length for i in self.spectra])
        if len(unique_lengths) > 1:
            raise ValidationError(
                f"The spectra have different lenghts where they should be the same.\n\t{unique_lengths}"
            )
        return self


def get_mean_spectra_info(spectra: List[SpectrumDataLoader]) -> Dict:
    """retrieves the info dict from spec instances and merges dict in keys that have 1 common value"""

    all_spec_info = [spec.info for spec in spectra]
    _all_spec_info_merged = {k: val for i in all_spec_info for k, val in i.items()}
    _all_spec_info_sets = [
        (k, set([i.get(k, None) for i in all_spec_info])) for k in _all_spec_info_merged
    ]
    mean_spec_info = {
        k: list(val)[0] for k, val in _all_spec_info_sets if len(val) == 1
    }
    # logger.warning(f"get_mean_spectra_info failed for spectra {spectra}")
    # mean_spec_info = {}
    mean_spec_info.update({"mean_spectrum": True})
    return mean_spec_info


def calculate_mean_spectrum_from_spectra(
    spectra: List[SpectrumDataLoader],
) -> Dict[str, SpectrumData]:
    """retrieves the clean data from spec instances and makes lists of tuples"""

    try:
        spectra_regions = [i.clean_spectrum.spec_regions for i in spectra]
        mean_spec_regions = {}
        for window_name in spectra_regions[0].keys():
            regions_specs = [i[window_name] for i in spectra_regions]
            ramanshift_mean = np.mean([i.ramanshift for i in regions_specs], axis=0)
            intensity_mean = np.mean([i.intensity for i in regions_specs], axis=0)

            _data = {
                "ramanshift": ramanshift_mean,
                "intensity": intensity_mean,
                "label": regions_specs[0].label + "_mean",
                "window_name": window_name + "_mean",
            }
            mean_spec = SpectrumData(**_data)
            mean_spec_regions[window_name] = mean_spec

    except Exception:
        logger.warning(f"get_mean_spectra_prep_data failed for spectra {spectra}")
        mean_spec_regions = {}

    return mean_spec_regions


def get_best_guess_spectra_length(spectra: List[SpectrumDataLoader]) -> List:
    lengths = [i.spectrum_length for i in spectra]
    set_lengths = set(lengths)
    if len(set_lengths) == 1:
        #  print(f'Spectra all same length {set_lengths}')
        return spectra

    length_counts = [(i, lengths.count(i)) for i in set_lengths]
    best_guess_length = max(length_counts, key=itemgetter(1))[0]
    print(f"Spectra not same length {length_counts} took {best_guess_length}")
    # self._raw_spectra = self._spectra
    spectra = [spec for spec in spectra if spec.spectrum_length == best_guess_length]
    return spectra
