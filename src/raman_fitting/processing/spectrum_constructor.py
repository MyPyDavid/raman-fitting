#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 11:10:59 2021

@author: zmg
"""

import copy
import logging
from collections import namedtuple
from dataclasses import dataclass, field
from operator import itemgetter
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

# from .. import __package_name__

from raman_fitting.indexing.filedata_parser import SpectrumReader
from raman_fitting.processing.cleaner import (
    BaselineSubtractorNormalizer,
    Despiker,
    SpectrumMethods,
)
from raman_fitting.processing.spectrum_template import SpecTemplate, SpectrumWindows

# from .parser import Parser
logger = logging.getLogger(__name__)


@dataclass(order=True, frozen=False)
class SpectrumDataLoader:
    """
    Raman Spectrum Loader Dataclass, reads in the file and constructs a clean spectrum from the data.
    A sequence of steps is performed on the raw data from SpectrumReader.
    The steps/methods are: smoothening filter, despiking and baseline correction.
    """

    # IDEA Fix this class, simplify

    _fields = ("ramanshift", "intensity")
    # _spectrum_grp_cols = ['PAR_file','Segment #',EvRHE, 'RPM_DAC']
    file: Path = field(default=Path(Path.cwd().joinpath("empty.txt")))
    # sample_position: int = 0
    # ramanshift: np.array = field(default=np.array([]), init=False)
    # intensity: np.array = field(default=np.array([]), init=False)
    spectrum_length: int = field(default=0, init=False)
    info: Dict = field(default_factory=dict, repr=False)
    ovv: pd.DataFrame = field(default=pd.DataFrame(), repr=False)
    run_kwargs: Dict = field(default_factory=dict, repr=False)

    def __post_init__(self):

        self._qcnm = self.__class__.__qualname__

        self.register = {}  # this stores the data of each method as they are performed
        self.filtered_intensity = None
        self._despike = None
        self._baseline_corrected = None
        self.clean_data = None
        self.clean_df = {}  # dict of DataFrames
        self.register_df = pd.DataFrame()
        self._read_succes = False

        self.load_data_delegator()

    def register_spectrum(self, ramanshift, intensity, label):
        _spec = SpecTemplate(ramanshift, copy.deepcopy(intensity), label)
        self.register.update({label: _spec})

    def __getattr__(self, attr):
        """checks if attr is in instance dicts before raising error"""
        if attr in self.run_kwargs.keys():
            # FIXME CARE getting attributes from kwargs
            return self.run_kwargs.get(attr, None)
        elif attr in self.info.keys():
            return self.info.get(attr, None)
        else:
            raise AttributeError(
                f'Attribute "{attr}" is not in {self.run_kwargs.keys()} or {self.info.keys()}.'
            )

    def load_data_delegator(self):
        """calls the SpectrumReader class"""

        if self.info:
            FP_from_info = self.info.get("FilePath", None)
            if FP_from_info:
                if Path(FP_from_info) != self.file:
                    raise ValueError(
                        f"Mismatch in value for FilePath:\{self.file} != {FP_from_info}"
                    )
        else:
            self.info = {"FilePath": self.file}

        raw_spectrum = SpectrumReader(self.file)
        # print("======== ", raw_spectrum)

        self.register_spectrum(raw_spectrum.ramanshift, raw_spectrum.intensity, "raw")
        if raw_spectrum.spectrum_length > 0:
            self.spectrum_length = raw_spectrum.spectrum_length
            self.spectrum_methods_delegator()
        else:
            logger.warning(f"{self._qcnm} load data fail for:\n\t {self.file}")
        self.info = {**self.info, **self.run_kwargs}

    def spectrum_methods_delegator(self):
        self.filter_data(on_lbl="raw", out_lbl="filtered")
        self.despike(on_lbl="filtered", out_lbl="despiked")
        self.baseline_correction(on_lbl="despiked", out_lbl="clean_data")
        self.set_clean_data_df()
        self.set_df_from_register()

    def filter_data(self, on_lbl="raw", out_lbl="filtered"):
        _r, _int, _lbl = self.register.get(on_lbl)
        logger.debug(f"{self.file} try to filter len int({len(_int)}),({type(_int)})")
        filtered_intensity = SpectrumMethods.filtered_int(intensity=_int)
        self.filtered_intensity = filtered_intensity
        self.register_spectrum(_r, filtered_intensity, out_lbl)

    def despike(self, on_lbl="filtered", out_lbl="despiked"):
        _r, _int, _lbl = self.register.get(on_lbl)
        _despike = Despiker(_int)  # IDEA check for nan in array
        self._despike = _despike
        self.register_spectrum(_r, _despike.despiked_intensity, out_lbl)

    def baseline_correction(self, on_lbl="despiked", out_lbl="clean_data"):
        _r, _int, _lbl = self.register.get(on_lbl)
        _baseline_corrected = BaselineSubtractorNormalizer(_r, _int, label="despiked")
        self._baseline_corrected = _baseline_corrected

        _fullspec = _baseline_corrected.norm_data["full"]
        self.register_spectrum(_fullspec.ramanshift, _fullspec.intensity, out_lbl)
        self.clean_data = _baseline_corrected.norm_data

    def set_clean_data_df(self):

        self.clean_df = {
            k: pd.DataFrame(
                {"ramanshift": val.ramanshift, f"int_{self.SamplePos}": val.intensity}
            )
            for k, val in self.clean_data.items()
        }

    def set_df_from_register(self):
        _regdf = pd.DataFrame()
        for k, val in self.register.items():
            _spec = pd.DataFrame(
                {
                    "ramanshift": val.ramanshift,
                    f"{k}_int_{self.SampleID}_{self.SamplePos}": val.intensity,
                }
            )
            if _regdf.empty:
                _regdf = _spec
            else:
                _regdf = pd.merge_asof(_regdf, _spec, on="ramanshift")
        self.register_df = _regdf
        logger.debug(
            f"{self._qcnm} set_df_from_register len int({len(_regdf)}),({type(_regdf)})"
        )

    def plot_raw(self):
        _raw_lbls = [
            i
            for i in self.register_df.columns
            if not any(a in i for a in ["ramanshift", "clean_data"])
        ]
        self.register_df.plot(x="ramanshift", y=_raw_lbls)

    def split_data(self, on_lbl="filtered"):
        _r, _int, _lbl = self.register.get(on_lbl)  # unpacking data from register
        for windowname, limits in SpectrumWindows().items():
            ind = (_r >= np.min(limits)) & (_r <= np.max(limits))
            _intslice = _int[ind]
            label = f"{_lbl}_window_{windowname}"
            self.register_spectrum(_r, _intslice, label)


class SpectrumDataCollection:
    """
    This class takes in a collection of SpectrumDataLoader instances.
    It checks each member of the list and this enables the option
    to take the mean of several spectra from the same SampleID.
    """

    MeanSpecTemplate = namedtuple(
        "MeanSpectras", "windowname sID_rawcols sIDmean_col mean_info mean_spec"
    )

    def __init__(self, spectra: List = [SpectrumDataLoader]):
        self._qcnm = self.__class__.__qualname__
        self._spectra = spectra
        Validators.check_members(
            self._spectra
        )  # only raises warning when errors are found
        self.spectra = Validators.check_spectra_lengths(self._spectra)

        self.info = self.get_mean_spectra_info(self.spectra)
        self.info_df = pd.DataFrame(self.info, index=[0])
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
        except Exception as exc:
            logger.warning(f"get_mean_spectra_info failed for spectra {spectra}")
            mean_spec_info = {}

        mean_spec_info.update({"mean_spectrum": True})

        return mean_spec_info

    @staticmethod
    def get_mean_spectra_prep_data(spectra: List[SpectrumDataLoader]) -> Dict:
        """retrieves the clean data from spec instances and makes lists of tuples"""
        # and merges dict in keys that have 1 common value'''
        try:
            _all_spec = [
                spec
                for spec in spectra
                if hasattr(spec, "clean_data") and hasattr(spec, "SamplePos")
            ]

            _all_spec_clean_data_keys = {
                k for i in _all_spec for k in i.clean_data.keys()
            }

            clean_prep_data = {
                k: [(i.SamplePos, i.clean_data.get(k, None)) for i in _all_spec]
                for k in _all_spec_clean_data_keys
            }
        except Exception as exc:
            logger.warning(f"get_mean_spectra_prep_data failed for spectra {spectra}")
            clean_prep_data = {}

        return clean_prep_data

    def calc_mean(self):
        """Core function of the merging of spectra of different sample positions"""
        _merged_window_specs = {}
        _speclst = []
        _posmean_lbl_base = f'int_{self.info.get("SampleID")}_mean'
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

            _old_spec = self.MeanSpecTemplate(
                wndwnm, _pos_lbl_lst, _posmean_lbl, self.info_df, _merge_df
            )
            _speclst.append(_old_spec)

        self.fitting_spectra = _speclst
        self.mean_data = _merged_window_specs

    def __repr__(self):
        return f"{self.info}"


class Validators:
    """collection of validator for spectrum object"""

    @staticmethod
    def check_members(spectra: List[SpectrumDataLoader]):
        """checks member of lists"""
        _false_spectra = [
            spec
            for spec in spectra
            if type(spec) != SpectrumDataLoader or not hasattr(spec, "clean_data")
        ]
        if _false_spectra:
            logger.warning(
                f'_check_members not all spectra members are "SpectrumDataLoader" or missing clean_data attribute'
            )

    @staticmethod
    def check_spectra_lengths(spectra: List[SpectrumDataLoader]) -> List:
        lengths = [i.spectrum_length for i in spectra]
        set_lengths = set(lengths)
        if len(set_lengths) == 1:
            #  print(f'Spectra all same length {set_lengths}')
            pass
        else:
            length_counts = [(i, lengths.count(i)) for i in set_lengths]
            best_guess_length = max(length_counts, key=itemgetter(1))[0]
            print(f"Spectra not same length {length_counts} took {best_guess_length}")
            # self._raw_spectra = self._spectra
            spectra = [
                spec for spec in spectra if spec.spectrum_length == best_guess_length
            ]
        return spectra
