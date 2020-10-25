
from .fit_models import PeakTypeChooser,make_model_hints





# ====== SECOND ORDER PEAKS ======= #
class D4D4_peak():
    '''2nd order D4 peak '''
#        D2D2_mod = VoigtModel(prefix='D2D2_')
    def __init__(self, PeakType = 'Lorentzian', prefix='D4D4_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D4D4_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 2435,'min' : 2400, 'max' : 2550},
                    'sigma' : {'value' : 30,'min' : 1, 'max' : 200},
                    'amplitude' : {'value' : 2,'min' : 1E-03, 'max' : 100}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
#                    'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}}
        return settings

class D1D1_peak():
    '''2nd order D(1) peak, aka 2D
    2450 cm􀀀1 band, which has been attributed recently to a D + D” 
    band by Couzi et al. [61], the D + D’ (in literature, the wrong D + G label is often found [62]), the
    2D’ bands and the 2D + G band.
    1627 and 2742 cm􀀀1 bands as the D’ and 2D
    '''
    def __init__(self, PeakType = 'Lorentzian', prefix='D1D1_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D1D1_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 2650,'min' : 2600, 'max' : 2750},
                    'sigma' : {'value' : 60,'min' : 1, 'max' : 200},
                    'amplitude' : {'value' : 14,'min' : 1E-03, 'max' : 100}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
            
        return settings

class GD1_peak():
    '''2nd order G+D(1) peak '''
#        D2D2_mod = VoigtModel(prefix='D2D2_')
    def __init__(self, PeakType = 'Lorentzian', prefix='GD1_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = GD1_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 2900,'min' : 2800, 'max' : 2950},
                    'sigma' : {'value' : 50,'min' : 1, 'max' : 200},
                    'amplitude' : {'value' : 10,'min' : 1E-03, 'max' : 100}}
        if GammaVary:
            setttings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings

class D2D2_peak():
    '''2nd order D2 peak, aka 2D2'''
#        D2D2_mod = VoigtModel(prefix='D2D2_')
    def __init__(self, PeakType = 'Lorentzian', prefix='D2D2_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D2D2_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 3250,'min' : 3000, 'max' : 3400},
                    'sigma' : {'value' : 60,'min' : 20, 'max' : 200},
                    'amplitude' : {'value' : 1,'min' : 1E-03, 'max' : 100}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings
# ====== SECOND ORDER PEAKS ======= #