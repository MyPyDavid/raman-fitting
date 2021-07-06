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

from .. import __package_name__
from .cleaner import BaselineSubtractorNormalizer, Despiker, SpectrumMethods
from .spectrum_template import SpecTemplate, SpectrumWindows

# from .parser import Parser
logger = logging.getLogger(__package_name__)


@dataclass(order=True, frozen=False)
class SpectrumDataLoader:
    """
    Raman Spectrum Loader Dataclass, reads in the file and constructs a spectrum from the data.
    """

    # TODO Fix this class, simplify

    _fields = ("ramanshift", "intensity")
    # _spectrum_grp_cols = ['PAR_file','Segment #',EvRHE, 'RPM_DAC']
    file: Path = field(default=Path(Path.cwd().joinpath("empty.txt")))
    # sample_position: int = 0
    # ramanshift: np.array = field(default=np.array([]), init=False)
    # intensity: np.array = field(default=np.array([]), init=False)
    spectrum_length: int = field(default=0, init=False)
    info: Dict = field(default_factory=dict, repr=False)
    ovv: type(pd.DataFrame) = field(default=pd.DataFrame(), repr=False)
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

    def __getattr__(self, value):

        if value in self.run_kwargs.keys():
            return self.run_kwargs.get(value, None)
        else:
            # super().__getattr__(value)
            raise AttributeError(f'Attribute "{value}" is not in class.')

    def load_data_delegator(self):

        if self.file.exists():
            self.info = {"FilePath": self.file}
            self.load_data()
            if self._read_succes:
                self.spectrum_methods_delegator()
            else:
                logger.warning("{self._qcnm} load data fail for:\n\t {self.file}")

            self.info = {**self.info, **self.run_kwargs}

        elif self.file.name == "empty.txt":
            print(f'Default empty.txt File: "{self.file}" ')
        else:
            raise ValueError(f'File: "{self.file}" does not exist.')

    def load_data(self, on_lbl="raw"):
        # assert self.file.exists(), f'File: "{self.file}" does not exist.'
        # TODO import file reader class here
        ramanshift, intensity = np.array([]), np.array([])
        i = 0
        while not ramanshift.any() and i < 2000:
            try:
                ramanshift, intensity = np.loadtxt(
                    self.file, usecols=(0, 1), delimiter="\t", unpack=True, skiprows=i
                )
                # Alternative parsing method with pandas.read_csv
                # _rawdf = pd.read_csv(self.file, usecols=(0, 1), delimiter='\t',
                #                     skiprows=i, header =None, names=['ramanshift','intensity'])
                logger.info(
                    f"{self.file} with len rs({len(ramanshift)}) and len int({len(intensity)})"
                )

                self._read_succes = True
                self.spectrum_length = len(ramanshift)
                self.info.update(
                    {"spectrum_length": self.spectrum_length, "skipped_rows": i}
                )
            except ValueError:
                i += 1
        self.register_spectrum(ramanshift, intensity, on_lbl)
        # self.ramanshift = ramanshift
        # self.intensity = intensity
        # self.register_spectrum(ramanshift,)

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
        _despike = Despiker(_int)  # TODO check for nan in array
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
            for i in self.regdf.columns
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

    def __init__(self, spectra: List = []):
        self._qcnm = self.__class__.__qualname__
        self._spectra = spectra
        self._check_members()
        self.test_spectra_lengths()
        self.get_merged_mean_info()
        self.calc_mean()

    def _check_members(self):
        # TODO remove assert and implement RaiseSpectrum error
        if not all(
            type(spec).__name__ == "SpectrumDataLoader" for spec in self._spectra
        ):
            _false_spectra = [
                spec
                for spec in self._spectra
                if not type(spec).__name__ == "SpectrumDataLoader"
            ]

            logger.warning(
                f'{self._qcnm} not all spectra members are "SpectrumDataLoader"'
            )

        if not all(hasattr(spec, "clean_data") for spec in self._spectra):
            logger.warning(
                f"{self._qcnm} not all spectra members are have attribute clean_data"
            )

    def test_spectra_lengths(self):
        lengths = [i.spectrum_length for i in self._spectra]
        set_lengths = set(lengths)
        if len(set_lengths) == 1:
            #  print(f'Spectra all same length {set_lengths}')
            pass
        else:
            length_counts = [(i, lengths.count(i)) for i in set_lengths]
            best_guess_length = max(length_counts, key=itemgetter(1))[0]
            print(f"Spectra not same length {length_counts} took {best_guess_length}")
            self._raw_spectra = self._spectra
            self._spectra = [
                spec
                for spec in self._spectra
                if spec.spectrum_length == best_guess_length
            ]

    def get_merged_mean_info(self):
        _d = {}  # spec info dict
        _cdks = {}  # clean data keys
        _prep_data = {}
        _info_df_lst = []
        for spec in self._spectra:

            if hasattr(spec, "info"):
                if not _d:
                    _d = spec.info
                else:
                    _d = {
                        x: _d[x] for x in _d if x in spec.info and _d[x] == spec.info[x]
                    }
                _info_df_lst.append(spec.info)

            if hasattr(spec, "clean_data"):
                if not _cdks:
                    _cdks = set(spec.clean_data.keys())

                else:
                    _cdks = {x for x in _cdks if x in set(spec.clean_data.keys())}

                if not _prep_data:
                    _prep_data = {
                        key: [(spec.SamplePos, val)]
                        for key, val in spec.clean_data.items()
                    }

                else:
                    for key, val in spec.clean_data.items():
                        _prep_data.get(key).append((spec.SamplePos, val))

        _d.update({"mean_spectrum": True})
        self.prep_clean_data = _prep_data
        self.info = _d
        self.info_df = pd.DataFrame(_info_df_lst)

    def calc_mean(self):
        """Core function of the merging of spectra of different sample positions"""
        assert hasattr(self, "prep_clean_data")  # TODO remove

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
