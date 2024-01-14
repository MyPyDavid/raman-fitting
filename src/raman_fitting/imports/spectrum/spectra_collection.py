import logging
from collections import namedtuple
from operator import itemgetter
from typing import Dict, List

# import pandas as pd
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
        # breakpoint()
        if not all(hasattr(spec, "clean_spectrum") for spec in self.spectra):
            raise ValidationError("missing clean_data attribute")
        return self

    @model_validator(mode="after")
    def check_spectra_lengths(self) -> "SpectraDataCollection":
        # breakpoint()
        lengths = [i.spectrum_length for i in self.spectra]
        if len(lengths) == 1:
            return self
        set_lengths = set(lengths)
        if len(set_lengths) > 1:
            raise ValidationError(
                f"The spectra have different lenghts where they should be the same.\n\t{set_lengths}"
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
        spectra_windows = [i.clean_spectrum.spec_windows for i in spectra]
        mean_spec_windows = {}
        for window_name in spectra_windows[0].keys():
            windows_specs = [i[window_name] for i in spectra_windows]
            ramanshift_mean = np.mean([i.ramanshift for i in windows_specs], axis=0)
            intensity_mean = np.mean([i.intensity for i in windows_specs], axis=0)

            _data = {
                "ramanshift": ramanshift_mean,
                "intensity": intensity_mean,
                "label": windows_specs[0].label + "_mean",
                "window_name": window_name + "_mean",
            }
            mean_spec = SpectrumData(**_data)
            mean_spec_windows[window_name] = mean_spec

    except Exception:
        logger.warning(f"get_mean_spectra_prep_data failed for spectra {spectra}")
        mean_spec_windows = {}

    return mean_spec_windows


class SpectrumDataCollection:
    """
    This class takes in a collection of SpectrumDataLoader instances.
    It checks each member of the list and this enables the option
    to take the mean of several spectra from the same SampleID.
    """

    # TODO change to pydantic model

    MeanSpecTemplate = namedtuple(
        "MeanSpectras", "windowname sID_rawcols sIDmean_col mean_info mean_spec"
    )

    def __init__(self, spectra: List = [SpectrumDataLoader]):
        self._qcnm = self.__class__.__qualname__
        self._spectra = spectra
        # Validators.check_members(
        #     self._spectra
        # )  # only raises warning when errors are found
        # self.spectra = Validators.check_spectra_lengths(self._spectra)

        self.info = self.get_mean_spectra_info(self.spectra)
        # self.info_df = pd.DataFrame(self.info, index=[0])
        self.prep_clean_data = self.get_mean_spectra_prep_data(self.spectra)

        self.calc_mean()

    @staticmethod
    def get_mean_spectra_info(spectra: List[SpectrumDataLoader]) -> Dict:
        """retrieves the info dict from spec instances and merges dict in keys that have 1 common value"""

        try:
            _all_spec_info = [spec.info for spec in spectra if hasattr(spec, "info")]

            _all_spec_info_merged = {
                k: val for i in _all_spec_info for k, val in i.items()
            }

            _all_spec_info_sets = [
                (k, set([i.get(k, None) for i in _all_spec_info]))
                for k in _all_spec_info_merged
            ]

            mean_spec_info = {
                k: list(val)[0] for k, val in _all_spec_info_sets if len(val) == 1
            }
        except Exception:
            logger.warning(f"get_mean_spectra_info failed for spectra {spectra}")
            mean_spec_info = {}

        mean_spec_info.update({"mean_spectrum": True})

        return mean_spec_info

    def calc_mean(self, sample_id: str):
        """Core function of the merging of spectra of different sample positions"""
        import pandas as pd

        _merged_window_specs = {}
        _speclst = []
        _posmean_lbl_base = f"int_{sample_id}_mean"
        for wndwnm, data in self.prep_clean_data.items():
            _merge_df = pd.DataFrame()
            _pos_lbl_lst = []

            for _pos, _sp in data:
                _pos_lbl = f"int_{_pos}"

                _dfspec = pd.DataFrame(
                    {"ramanshift": _sp.ramanshift, _pos_lbl: _sp.intensity}
                )

                if _merge_df.empty:
                    _merge_df = _dfspec
                else:
                    _merge_df = pd.merge_asof(_merge_df, _dfspec, on="ramanshift")
                _pos_lbl_lst.append(_pos_lbl)

            _posmean_lbl = f"{_posmean_lbl_base}_{len(_pos_lbl_lst)}"
            _merge_df = _merge_df.assign(
                **{_posmean_lbl: _merge_df[_pos_lbl_lst].mean(axis=1)}
            )
            _merged_window_specs.update({wndwnm: _merge_df})

            # _old_spec = self.MeanSpecTemplate(
            #     wndwnm, _pos_lbl_lst, _posmean_lbl, self.info_df, _merge_df
            # )
            _speclst.append(_merged_window_specs)  # TODO remove

        self.fitting_spectra = _speclst
        self.mean_data = _merged_window_specs

    def __repr__(self):
        return f"{self.info}"


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
