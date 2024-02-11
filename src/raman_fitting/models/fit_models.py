import datetime as dt
import logging
from collections import OrderedDict, namedtuple
from typing import Dict
import time

import pandas as pd
from pydantic import BaseModel, model_validator, Field, ConfigDict
from lmfit import Model as LMFitModel
from lmfit.model import ModelResult

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.spectrum import SpectrumData

logger = logging.getLogger(__name__)


class SpectrumFitModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    spectrum: SpectrumData
    model: BaseLMFitModel
    fit_kwargs: Dict = Field(default_factory=dict)
    fit_result: ModelResult = Field(None, init_var=False)
    elapsed_time: float = Field(0, init_var=False, repr=False)

    @model_validator(mode="after")
    def match_window_names(self):
        model_window = self.model.window_name
        spec_window = self.spectrum.window_name
        if model_window != spec_window:
            raise ValueError(
                f"Window names do not match {model_window} and {spec_window}"
            )
        return self

    def run_fit(self) -> ModelResult:
        if not self.fit_kwargs:
            self.fit_kwargs.update(**{"method": "leastsq"})
        lmfit_model = self.model.lmfit_model
        start_time = time.time()
        fit_result = run_fit(lmfit_model, self.spectrum, **self.fit_kwargs)
        end_time = time.time()
        elapsed_seconds = abs(start_time - end_time)
        self.elapsed_time = elapsed_seconds
        self.fit_result = fit_result


def run_fit(
    model: LMFitModel, spectrum: SpectrumData, method="leastsq", **kws
) -> ModelResult:
    # ideas: improve fitting loop so that starting parameters from modelX and modelX+Si are shared, faster...
    init_params = model.make_params()
    x, y = spectrum.ramanshift, spectrum.intensity
    out = model.fit(y, init_params, x=x, method=method)  # 'leastsq'
    return out


class Fitter:
    """
    Fitter class for executing the fitting functions and optimizations

    IDEA: implement sensing of spectrum for Si samples
    """

    fit_windows = ["first_order", "second_order"]

    def __init__(self, spectra_arg, models=None, start_fit=True):
        self._qcnm = self.__class__.__qualname__
        logger.debug(f"{self._qcnm} is called with spectrum\n\t{spectra_arg}\n")
        self.start_fit = start_fit
        self.models = models

        self.spectra_arg = spectra_arg
        self.spectra = spectra_arg
        self.fit_delegator()

    @property
    def spectra(self):
        return self._spectra

    @spectra.setter
    def spectra(self, value):
        """Checks if value is dict or else takes a dict from class instance value"""

        _errtxt = f"This assignment {value} does not contain valid spectra"
        if isinstance(value, dict):
            _data = value
        elif isinstance(value, "SpectrumDataCollection"):
            _data = value.mean_data
            _fit_lbl = "mean"
        elif isinstance(value, "SpectrumDataLoader"):
            _data = value.clean_df
            _fit_lbl = "int"
        else:
            raise ValueError(_errtxt)

        _specs = {
            k: val
            for k, val in _data.items()
            if k in self.fit_windows and isinstance(val, pd.DataFrame)
        }
        # assert bool(_specs), _errtxt
        if not _specs:
            self.start_fit = False

        self._spectra = _specs
        self.FitResults = {}
        info = {}
        if hasattr(value, "info"):
            info = {**info, **value.info}
        self.info = info

    def fit_delegator(self):
        if self.start_fit:
            logger.info(
                f"\n{self._qcnm} is starting to fit the models on spectrum:\n\t{self.info.get('SampleID','no name')}"
            )

            self.fit_models(self.models.second_order)  # second order should go first
            logger.info(
                f"\t - second order finished, {len(self.models.second_order)} model"
            )
            # rum:\t{self.info.get('SampleID','no name')}\n")
            self.fit_models(self.models.first_order)
            logger.info(
                f"\t - first order finished, {len(self.models.first_order)} models"
            )

    def fit_models(self, model_selection):
        _fittings = {}
        logger.debug(f"{self._qcnm} fit_models starting.")
        for modname, model in model_selection.items():
            modname, model
            _windowname = [i for i in self.fit_windows if modname[0:3] in i][0]
            _data = self.spectra.get(_windowname)
            _int_lbl = self.get_int_label(_data)
            try:
                out = self.run_fit(
                    model.lmfit_model,
                    _data,
                    _int_lbl=_int_lbl,
                    _modelname=modname,
                    _info=self.info,
                )
                prep = PrepareParams(out, extra_fit_results=self.FitResults)
                _fittings.update({modname: prep.FitResult})
            except Exception as e:
                logger.warning(
                    f"{self._qcnm} fit_model failed for {modname}: {model}, because:\n {e}"
                )

        self.FitResults.update(**_fittings)

    def run_fit(self, model, _data, method="leastsq", **kws):
        # ideas: improve fitting loop so that starting parameters from modelX and modelX+Si are shared, faster...
        init_params = model.make_params()
        x, y = _data.ramanshift, _data[kws.get("_int_lbl")]
        out = model.fit(y, init_params, x=x, method=method)  # 'leastsq'
        for k, val in kws.items():
            if not hasattr(out, k):
                _attrkey = k
            elif not hasattr(out, f"_{k}"):
                _attrkey = f"_{k}"
            else:
                _attrkey = None
            if _attrkey:
                setattr(out, _attrkey, val)
        return out

    def get_int_label(self, value: pd.DataFrame):
        _lbl = ""
        if not isinstance(value, pd.DataFrame):
            return _lbl
        cols = [i for i in value.columns if "ramanshift" not in i]
        if not cols:
            return _lbl

        if len(cols) == 1:
            _lbl = cols[0]
        elif len(cols) > 1:
            if any("mean" in i for i in cols):
                _lbl = [i for i in cols if "mean" in i][0]
            elif any("int" in i for i in cols):
                _lbl = [i for i in cols if "int" in i][0]
        return _lbl


class PrepareParams:
    fit_attr_export_lst = (
        "chisqr",
        "redchi",
        "bic",
        "aic",
        "method",
        "message",
        "success",
        "nfev",
    )
    fit_result_template = namedtuple(
        "FitResult",
        [
            "FitComponents",
            "FitParameters",
            "FitReport",
            "extrainfo",
            "model_name",
            "raw_data_col",
        ],
    )
    ratio_params = [("I", "_height"), ("A", "_amplitude")]
    _standard_2nd_order = "2nd_4peaks"

    def __init__(self, model_result, extra_fit_results={}):
        self._qcnm = self.__class__.__qualname__
        logger.debug(f"{self._qcnm} is called with model_result\n\t{model_result}\n")
        self.extra_fit_results = extra_fit_results
        self.model_result = model_result

    @property
    def model_result(self):
        return self._model_result

    @model_result.setter
    def model_result(self, value):
        """
        Takes the ModelResult class instance from lmfit.
        Optional extra functionality with a list of instances.
        """
        self.result = {}

        if "ModelResult" in type(value).__name__:
            self.result.update(value.params.valuesdict())
            self.comps = value.model.components
        elif ("list" or "tuple") in type(value).__name__:
            assert all("ModelResult" in type(i).__name__ for i in value)
            [self.result.update(mod.params.valuesdict()) for mod in value]
            self.comps = [i for mod in value for i in mod.model.components]

        self.peaks = set(
            [i.prefix for i in self.comps]
        )  # peaks is prefix from components

        _mod_lbl = "Model"
        if hasattr(value, "_modelname"):
            _mod_lbl = f'Model_{getattr(value,"_modelname")}'
        self.model_name_lbl = _mod_lbl

        self.raw_data_lbl = value._int_lbl

        self._model_result = value

        self.make_result()

    def make_result(self):
        self.prep_params()
        self.prep_components()
        self.FitReport = self.model_result.fit_report(show_correl=False)

        self.extra_info = {}
        self.prep_extra_info()
        self.FitResult = self.fit_result_template(
            self.FitComponents,
            self.FitParameters,
            self.FitReport,
            self.extra_info,
            self.model_name_lbl,
            self.raw_data_lbl,
        )

    def prep_extra_info(self):
        self.extra_info = {}
        _destfitcomps = self.model_result._info["DestFittingComps"]
        _model_destdir = _destfitcomps.joinpath(
            f'{self.model_name_lbl}_{self.model_result._info["SampleID"]}'
        )
        self.extra_info = {
            **self.model_result._info,
            **{"DestFittingModel": _model_destdir},
        }

    def prep_params(self):
        fit_attrs = OrderedDict(
            zip(
                [f"lmfit_{i}" for i in self.fit_attr_export_lst],
                [getattr(self.model_result, i) for i in self.fit_attr_export_lst],
            )
        )
        self.result.update(fit_attrs)
        try:
            self.add_ratio_params()
        except Exception as e:
            logger.error(f"{self._qcnm} extra prep params failed\n\t{e}\n")

        self.result.update(
            {"_run_date_YmdH": dt.datetime.now().strftime(format="%Y-%m-%d %H:00")}
        )
        self.FitParameters = pd.DataFrame(self.result, index=[self.model_name_lbl])

    def prep_components(self):
        # FittingParams = pd.DataFrame(fit_params_od,index=[peak_model])
        _fit_comps_data = OrderedDict({"RamanShift": self.model_result.userkws["x"]})
        _fit_comps_data.update(self.model_result.eval_components())

        # IDEA take out
        # print('===/n',self.model_result, '/n')
        # print('===/n',self.model_result.__dict__.keys(), '/n')

        _fit_comps_data.update(
            {
                self.model_name_lbl: self.model_result.best_fit,
                "residuals": self.model_result.residual,
                self.model_result._int_lbl: self.model_result.data,
            }
        )
        FittingComps = pd.DataFrame(_fit_comps_data)
        self.FitComponents = FittingComps


def NormalizeFit(model: LMFitModel, norm_cleaner, plotprint=False):  # pragma: no cover
    # IDEA: optional add normalization seperately to Fitter
    x, y = norm_cleaner.spec.ramanshift, norm_cleaner.blcorr_desp_intensity
    # Model = InitializeModels("2peaks normalization Lorentzian")
    params = model.make_params()
    pre_fit = model.fit(y, params, x=x)  # 'leastsq'
    IG, ID = pre_fit.params["G_height"].value, pre_fit.params["D_height"].value
    output = {
        "factor": 1 / IG,
        "ID/IG": ID / IG,
        "ID": ID,
        "IG": IG,
        "G_center": pre_fit.params["G_center"].value,
        "D_center": pre_fit.params["D_center"].value,
        "Model": model,
    }
    #    pre_fit = Model.fit(y,params ,x=x,method='differential-evolution') # 'leastsq'
    if plotprint:
        pre_fit.plot()
        print(pre_fit.fit_report())
    return output


if __name__ == "__main__":
    from raman_fitting.config.settings import settings

    test_fixtures = list(settings.internal_paths.example_fixtures.glob("*txt"))
    file = [i for i in test_fixtures if "_pos4" in i.stem][0]
    from raman_fitting.imports.spectrumdata_parser import SpectrumReader

    specread = SpectrumReader(file)

    from raman_fitting.processing.post_processing import SpectrumProcessor

    spectrum_processor = SpectrumProcessor(specread.spectrum)
    clean_spec_1st_order = spectrum_processor.clean_spectrum.spec_windows[
        "savgol_filter_raw_window_first_order"
    ]
    clean_spec_1st_order.window_name = "first_order"

    from raman_fitting.models.deconvolution.base_model import (
        get_models_and_peaks_from_definitions,
    )

    models = get_models_and_peaks_from_definitions()
    model_2peaks = models["first_order"]["2peaks"]
    spec_fit = SpectrumFitModel(
        **{"spectrum": clean_spec_1st_order, "model": model_2peaks}
    )
    spec_fit.run_fit()
    print(spec_fit.fit_result.best_values)
    spec_fit.fit_result.plot(show_init=True)
