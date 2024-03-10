from typing import TypeAlias, Dict

from raman_fitting.models.deconvolution.base_model import BaseLMFitModel
from raman_fitting.models.fit_models import SpectrumFitModel

LMFitModelCollection: TypeAlias = Dict[str, Dict[str, BaseLMFitModel]]
SpectrumFitModelCollection: TypeAlias = Dict[str, Dict[str, SpectrumFitModel]]
