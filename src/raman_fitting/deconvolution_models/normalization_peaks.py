''' Peaks used for normalization'''

if __name__ in ('__main__', 'normalization_peaks'):
    from base_peak import BasePeak
else:
    from .base_peak import BasePeak

# ====== PEAKS USED FOR NORMALIZATION ======= #

class norm_G_peak(metaclass=BasePeak):
    '''G_peak used for normalization'''

    def __init__(self, *args, **kwargs):
        self.peak_name = 'norm_G'
        self.peak_type = 'Lorentzian'
        self.input_param_settings = {
            'center': {'value': 1581, 'min': 1500, 'max': 1600},
            'sigma': {'value': 40, 'min': 1E-05, 'max': 1E3},
            'amplitude': {'value': 8E4, 'min': 1E2}}
    # norm_G_peak = BasePeak(peak_name=peak_name,peak_type=peak_type,input_param_settings=settings)

class norm_D_peak(metaclass=BasePeak):
    ''' D_peak for normalization '''

    def __init__(self, *args, **kwargs):
        self.peak_name='norm_D'
        self.peak_type='Lorentzian'
        self.input_param_settings={
            'center': {'value': 1350,'min': 1300, 'max': 1400},
            'sigma': {'value': 90, 'min': 1E-05},
            'amplitude': {'value': 10E5, 'min': 1E2}}
        