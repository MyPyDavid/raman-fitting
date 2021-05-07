


if __name__ == '__main__':
    
    from base_peak import BasePeak # for testing purposes

else:
    
    from .base_peak import BasePeak

# ====== SECOND ORDER PEAKS ======= #
class D4D4_peak(BasePeak):
    '''2nd order D4 peak '''
#        D2D2_mod = VoigtModel(prefix='D2D2_')

    def __init__(self, peak_type = 'Lorentzian', peak_name ='D4D4', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):
        settings = {'center' : {'value' : 2435,'min' : 2400, 'max' : 2550},
                    'sigma' : {'value' : 30,'min' : 1, 'max' : 200},
                    'amplitude' : {'value' : 2,'min' : 1E-03, 'max' : 100}}
        return settings

class D1D1_peak(BasePeak):
    '''2nd order D(1) peak, aka 2D
    2450 cm􀀀1 band, which has been attributed recently to a D + D” 
    band by Couzi et al. [61], the D + D’ (in literature, the wrong D + G label is often found [62]), the
    2D’ bands and the 2D + G band.
    1627 and 2742 cm􀀀1 bands as the D’ and 2D
    '''
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='D1D1', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):
        settings = {'center' : {'value' : 2650,'min' : 2600, 'max' : 2750},
                    'sigma' : {'value' : 60,'min' : 1, 'max' : 200},
                    'amplitude' : {'value' : 14,'min' : 1E-03, 'max' : 100}}
        return settings

class GD1_peak(BasePeak):
    '''2nd order G+D(1) peak '''
#        D2D2_mod = VoigtModel(prefix='D2D2_')
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='GD1', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):
        settings = {'center' : {'value' : 2900,'min' : 2800, 'max' : 2950},
                    'sigma' : {'value' : 50,'min' : 1, 'max' : 200},
                    'amplitude' : {'value' : 10,'min' : 1E-03, 'max' : 100}}
        return settings
    

class D2D2_peak(BasePeak):
    '''2nd order D2 peak, aka 2D2'''
#        D2D2_mod = VoigtModel(prefix='D2D2_')
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='D2D2', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):
        settings = {'center' : {'value' : 3250,'min' : 3000, 'max' : 3400},
                    'sigma' : {'value' : 60,'min' : 20, 'max' : 200},
                    'amplitude' : {'value' : 1,'min' : 1E-03, 'max' : 100}}
        return settings
# ====== SECOND ORDER PEAKS ======= #