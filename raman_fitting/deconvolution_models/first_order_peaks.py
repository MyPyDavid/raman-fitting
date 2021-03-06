

if __name__ == '__main__':
    
    from base_peak import BasePeak

else:
    # print(__name__)
    from .base_peak import BasePeak



class G_peak(BasePeak):
    '''Graphite belongs to the P63/mmc (D46h) space group. If considering only a graphene plane, at 
    the Ã point of the Brillouin zone, there are six normal modes that possess only one mode (doubly
    degenerate in plane) with a E2g representation, which is Raman active
    G ; Ideal graphitic lattice (E2g-symmetry)
    G peak center stable over different laser wavelengths. Influenced by potential, HSO4 adsorption (or ionization of G- and G+),
    magnetic fields, pressure
    Für G: 1580-1590 D5 und D2 weiß ich nicht
    '''
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='G', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )

    def input_param_settings(self):
        # TODO maybe read in param settings form eg xls file
        param_settings = {'center' : {'value' : 1571,'min' : 1545, 'max' : 1595},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
        return param_settings
   
    def normalization_param_settings(self):
        settings = {'center' : {'value' : 1581, 'min' : 1500, 'max' : 1600},
                    'sigma' : {'value' : 40, 'min' : 1E-05, 'max' : 1E3},
                    'amplitude' : {'value' : 8E4, 'min' : 1E2}}
        return settings

    
def _testing():
    Gp = G_peak()
    Gp
    Gp.print_params()
    tp = test_peak()
    
    model = G_peak() + D_peak()


class D_peak(BasePeak):
    ''' D or D1 ; Disordered graphitic lattice (graphene layer edges,A1gsymmetry)
    A defective graphite presents other bands that can be as intense as the G band at D=1350 and D'=1615 cm-1
    These bands are activated by defects due to the breaking of the crystal symmetry that relax the Raman selection rules.
    Für D1: 1340-1350 
    '''

    def __init__(self, peak_type = 'Lorentzian', peak_name ='D', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):
        settings = {'center' : {'value' : 1350,'min' : 1330, 'max' : 1380},
                    'sigma' : {'value' : 35,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 120,'min' : 1E-05, 'max' : 500}}
        return settings
    
    def normalization_param_settings(self):
        settings = {'center' : {'value' : 1350,'min' : 1300, 'max' : 1400},
                    'sigma' : {'value' : 90, 'min' : 1E-05},
                    'amplitude' : {'value' : 10E5, 'min' : 1E2}}
        return settings


class D2_peak(BasePeak):
    '''D2 or D' ; Right next to the G peak, sometimes not obvious as G peak split.
    Disordered graphitic lattice (surface graphene layers,E2g-symmetry)
    j.molstruc.2010.12.065
    '''

    def __init__(self, peak_type = 'Lorentzian', peak_name ='D2', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):
         settings = {'center' : {'value' : 1606,'min' : 1592, 'max' : 1635},
                    'sigma' : {'value' : 30,'min' : 5, 'max' : 150},
                    'amplitude' : {'value' : 35,'min' : 5, 'max' : 500}}
         return settings
        

class D3_peak(BasePeak):
    ''' D3 or D'' or A or Am ; Between the D and G peak, sometimes too broad.
    For amorphous carbon (Gaussian[26]or Lorentzian[3,18,27]line shape).
    Für D3: 1495-1515
    '''
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='D3', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):
        settings = {'center' : {'value' : 1480, 'min' : 1450, 'max' : 1505},
                    'sigma' : {'value' : 25,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 25,'min' : 1E-02, 'max' : 500}}
        return settings

class D4_peak(BasePeak):
    ''' D4 or I ; Below D band, a shoulder sometimes split with D5 band.
    Disordered graphitic lattice (A1gsymmetry)[10],polyenes[3,27], ionic impurities
    D4 peak at 1212 cm−1
    Jurkiewicz, K., Pawlyta, M., Zygadło, D. et al. J Mater Sci (2018) 53: 3509. https://doi.org/10.1007/s10853-017-1753-7
    Für D4: 1185-1210, but depends on if there is D5 or not.
    '''

    def __init__(self, peak_type = 'Lorentzian', peak_name ='D4', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
        
    def input_param_settings(self):
        settings = {'center' : {'value' : 1230,'min' : 1180, 'max' : 1290},
                    'sigma' : {'value' : 40,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 20,'min' : 1E-02, 'max' : 200}}
        return settings
   
class D5_peak(BasePeak):
    '''D5 peak at 1110 cm−1. At lowest should of D peak, below D4.
    Ref: Jurkiewicz, K., Pawlyta, M., Zygadło, D. et al. J Mater Sci (2018) 53: 3509. https://doi.org/10.1007/s10853-017-1753-7
    '''
    
    def __init__(self, peak_type = 'Lorentzian', peak_name ='D5', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self):    
        settings = {'center' : {'value' : 1150,'min' : 1100, 'max' : 1200},
                    'sigma' : {'value' : 40,'min' : 1, 'max' : 150},
                    'amplitude' : {'value' : 20,'min' : 1E-02, 'max' : 200}}
        return settings

class Si1_peak(BasePeak):
    '''===== Extra peak at ca. 960 cm-1 presumably from Si substrate 2nd order === not from Nafion...
    => Either cut the Spectra 1000-2000
    => Place an extra Gaussian peak at 960 in the fit
    '''

    def __init__(self, peak_type = 'Gaussian', peak_name ='Si1', gammavary = False, normalization = False):
        # self.model = PeakTypeChooser(PeakType,prefix)
        super().__init__(peak_type = peak_type, peak_name = peak_name, gammavary = gammavary, normalization = normalization )
       
    def input_param_settings(self): 
        settings = {'center' : {'value' : 960,'min' : 900, 'max' : 980},
                    'sigma' : {'value' : 10,'min' : 0, 'max' : 150},
                    'amplitude' : {'value' : 10,'min' : 0, 'max' : 200}}
        return settings

def test_for_Si_substrate(model):
    '''make test fit for only slice 900-1000'''