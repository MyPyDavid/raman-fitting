
from fit_models import PeakTypeChooser,make_model_hints




'''
Notes:
Für D1: 1340-1350 Für D3: 1495-1515
Für G: 1580-1590 D5 und D2 weiß ich nicht
'''

class G_peak():
    '''Graphite belongs to the P63/mmc (D46h) space group. If considering only a graphene plane, at 
    the Ã point of the Brillouin zone, there are six normal modes that possess only one mode (doubly
    degenerate in plane) with a E2g representation, which is Raman active
    G ; Ideal graphitic lattice (E2g-symmetry)
    G peak center stable over different laser wavelengths. Influenced by potential, HSO4 adsorption (or ionization of G- and G+),
    magnetic fields, pressure
    '''
    def __init__(self, PeakType = 'Lorentzian', prefix='G_', GammaVary = False, normalization = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = G_peak.param_hints(GammaVary, normalization)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary, normalization ):
        settings = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        if normalization:
             settings = {'center' : {'value' : 1581, 'min' : 1500, 'max' : 1600},
                    'sigma' : {'value' : 40, 'min' : 1E-05},
                    'amplitude' : {'value' : 8E4, 'min' : 1E2}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings
    

class D_peak():
    ''' D or D1 ; Disordered graphitic lattice (graphene layer edges,A1gsymmetry)
    A defective graphite presents other bands that can be as intense as the G band at D=1350 and D'=1615 cm-1
    These bands are activated by defects due to the breaking of the crystal symmetry that relax the Raman selection rules'''

    def __init__(self, PeakType = 'Lorentzian', prefix='D_', GammaVary = False,normalization = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D_peak.param_hints(GammaVary, normalization)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary,normalization):
        settings = {'center' : {'value' : 1350,'min' : 1330, 'max' : 1380},
                    'sigma' : {'value' : 35,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 120,'min' : 1E-05, 'max' : 500}}
        if normalization:
             settings = {'center' : {'value' : 1350,'min' : 1300, 'max' : 1400},
                    'sigma' : {'value' : 90, 'min' : 1E-05},
                    'amplitude' : {'value' : 10E5, 'min' : 1E2}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})

        return settings


class D2_peak():
    '''D2 or D' ; Right next to the G peak, sometimes not obvious as G peak split.
    Disordered graphitic lattice (surface graphene layers,E2g-symmetry)
    j.molstruc.2010.12.065'''

    def __init__(self, PeakType = 'Lorentzian', prefix='D2_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D2_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 1606,'min' : 1592, 'max' : 1635},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings

class D3_peak():
    ''' D3 or D'' or A or Am ; Between the D and G peak, sometimes too broad.
    For amorphous carbon (Gaussian[26]or Lorentzian[3,18,27]line shape)'''

    def __init__(self, PeakType = 'Lorentzian', prefix='D3_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D3_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 1480, 'min' : 1450, 'max' : 1505},
                    'sigma' : {'value' : 25,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 25,'min' : 1E-02, 'max' : 500}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings

class D4_peak():
    ''' D4 or I ; Below D band, a shoulder sometimes split with D5 band.
    Disordered graphitic lattice (A1gsymmetry)[10],polyenes[3,27], ionic impurities
    D4 peak at 1212 cm−1
    Jurkiewicz, K., Pawlyta, M., Zygadło, D. et al. J Mater Sci (2018) 53: 3509. https://doi.org/10.1007/s10853-017-1753-7
    Für D4: 1185-1210, but depends on if there is D5 or not'''

    def __init__(self, PeakType = 'Lorentzian', prefix='D4_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D4_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 1230,'min' : 1180, 'max' : 1290},
                    'sigma' : {'value' : 40,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 20,'min' : 1E-02, 'max' : 200}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings
   
class D5_peak():
    '''D5 peak at 1110 cm−1. At lowest should of D peak, below D4.
    Ref: Jurkiewicz, K., Pawlyta, M., Zygadło, D. et al. J Mater Sci (2018) 53: 3509. https://doi.org/10.1007/s10853-017-1753-7
    '''
    def __init__(self, PeakType = 'Lorentzian', prefix='D5_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = D5_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 1150,'min' : 1100, 'max' : 1200},
                    'sigma' : {'value' : 40,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 20,'min' : 1E-02, 'max' : 200}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings

class Si_substrate_peak():
    '''===== Extra peak at ca. 960 cm-1 presumably from Si substrate 2nd order === not from Nafion...
    => Either cut the Spectra 1000-2000
    => Place an extra Gaussian peak at 960 in the fit
    '''
    def __init__(self, PeakType = 'Gaussian', prefix='Si_substrate_', GammaVary = False):
        self.model = PeakTypeChooser(PeakType,prefix)
        self.param_hints = Si_substrate_peak.param_hints(GammaVary)
        self.mod = make_model_hints(self.model,self.param_hints)
        
    def param_hints(GammaVary):
        settings = {'center' : {'value' : 960,'min' : 900, 'max' : 980},
                    'sigma' : {'value' : 10,'min' : 0, 'max' : 150},
                    'amplitude' : {'value' : 10,'min' : 0, 'max' : 200}}
        if GammaVary:
            settings.update({'gamma' : {'value' : 1,'min' : 1E-05, 'max' : 70, 'vary' : GammaVary}})
        return settings

def test_for_Si_substrate(model):
    '''make test fit for only slice 900-1000