import logging

logger = logging.getLogger(__name__)


from .splitter import get_default_spectrum_windows


class BaselineSubtractorNormalizer:
    """
    For baseline subtraction as well as normalization of a spectrum
    """

    def __init__(self, *args, **kws):
        self.split_spectrum_data_in_windows()
        self.windowlimits = get_default_spectrum_windows()
        blcorr_data, blcorr_info = self.subtract_loop()
        self.blcorr_data = blcorr_data
        self.blcorr_info = blcorr_info
        normalization_intensity = self.get_normalization_factor()
        self.norm_factor = 1 / normalization_intensity
        self.norm_data = self.normalize_data(self.blcorr_data, self.norm_factor)

    def subtract_loop(self):
        _blcorr = {}
        _info = {}
        for windowname, spec in self.windows_data.items():
            blcorr_int, blcorr_lin = self.subtract_baseline_per_window(windowname, spec)
            label = f"blcorr_{windowname}"
            if self.label:
                label = f"{self.label}_{label}"
            _data = self.data(spec.ramanshift, blcorr_int, label)
            _blcorr.update(**{windowname: _data})
            _info.update(**{windowname: blcorr_lin})
        return _blcorr, _info

    def subtract_baseline_per_window(self, windowname, spec):
        rs = spec.ramanshift
        if not rs.any():
            return spec.intensity, (0, 0)

        if windowname[0:4] in ("full", "norm"):
            i_fltrd_dspkd_fit = self.windows_data.get("1st_order").intensity
        else:
            i_fltrd_dspkd_fit = spec.intensity
        _limits = self.windowlimits.get(windowname)

        bl_linear = linregress(
            rs[[0, -1]],
            [
                np.mean(i_fltrd_dspkd_fit[0 : _limits[0]]),
                np.mean(i_fltrd_dspkd_fit[_limits[1] : :]),
            ],
        )
        i_blcor = spec.intensity - (bl_linear[0] * rs + bl_linear[1])
        return i_blcor, bl_linear

    def get_normalization_factor(self, norm_method="simple") -> float:
        try:
            if norm_method == "simple":
                normalization_intensity = np.nanmax(
                    self.blcorr_data["normalization"].intensity
                )
            elif norm_method == "fit":
                # IDEA not implemented
                normalization = NormalizeFit(
                    self.blcorr_data["1st_order"], plotprint=False
                )  # IDEA still implement this NormalizeFit
                normalization_intensity = normalization["IG"]
            else:
                logger.warning(f"unknown normalization method {norm_method}")
                normalization_intensity = 1
        except Exception as exc:
            logger.error(f"normalization error {exc}")
            normalization_intensity = 1

        return normalization_intensity

    def normalize_data(self, data, norm_factor) -> dict:
        ret = {}
        for windowname, spec in data.items():
            label = f"norm_blcorr_{windowname}"
            if self.label:
                label = f"{self.label}_{label}"

            _data = self.data(spec.ramanshift, spec.intensity * self.norm_factor, label)
            ret.update(**{windowname: _data})
        return ret
