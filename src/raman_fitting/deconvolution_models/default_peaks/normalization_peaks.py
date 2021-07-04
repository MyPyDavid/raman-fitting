""" Peaks used for normalization"""

if __name__ == "__main__":
    from raman_fitting.deconvolution_models.base_peak import BasePeak
else:
    from .base_peak import BasePeak

__all__ = ["norm_G_peak", "norm_D_peak"]
# ====== PEAKS USED FOR NORMALIZATION ======= #


class norm_G_peak(metaclass=BasePeak):
    """G_peak used for normalization"""

    def __init__(self, *args, **kwargs):
        self.peak_name = "norm_G"
        self.peak_type = "Lorentzian"
        self.input_param_settings = {
            "center": {"value": 1581, "min": 1500, "max": 1600},
            "sigma": {"value": 40, "min": 1e-05, "max": 1e3},
            "amplitude": {"value": 8e4, "min": 1e2},
        }

    # norm_G_peak = BasePeak(peak_name=peak_name,peak_type=peak_type,input_param_settings=settings)


class norm_D_peak(metaclass=BasePeak):
    """D_peak for normalization"""

    def __init__(self, *args, **kwargs):
        self.peak_name = "norm_D"
        self.peak_type = "Lorentzian"
        self.input_param_settings = {
            "center": {"value": 1350, "min": 1300, "max": 1400},
            "sigma": {"value": 90, "min": 1e-05},
            "amplitude": {"value": 10e5, "min": 1e2},
        }
