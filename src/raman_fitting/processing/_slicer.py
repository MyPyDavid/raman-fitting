# flake8: noqa
# TODO remove this duplicate module

from collections import namedtuple

# from raman_fitting.processing.spectrum_constructor import SpectrumData

class SpectraInfo():
       '''takes namedtuple with spectra'''

       def __init__(self):
           self.window = SpectraInfo.SpectrumWindows()

       def SpectrumWindows():
           windows = {'full' : (200,3600), 'full_1st_2nd' : (800,3500), 'low' : (150,850), '1st_order' : (900,2000),
                      'mid' : (1850,2150), '2nd_order' : (2000,3380), 'normalization' : (1500,1675)}
           return windows

       def ramanshift_slice_indx(ramanshift, windowname):
           low,high = SpectraInfo().window[windowname]
           ind = (ramanshift >= low) & (ramanshift <= high)
           return ind

       def spec_slice(spec,windowname):
           ind = SpectraInfo.ramanshift_slice_indx(spec.ramanshift, windowname)

           _arrays = {i:getattr(spec, i) for i in spec._fields if 'array' in str(type(getattr(spec, i))) }

           if type(spec).__name__ == 'SpectrumData':
               _info = spec.info

           elif type(spec).__name__ == 'spectrum_normalized':
               _info = {i:getattr(spec, i) for i in spec._fields if not 'array' in str(type(getattr(spec, i))) }
               # _info = {}

           SpecSlice_template = namedtuple('SpectrumSliced',tuple(_arrays.keys())+('windowname',)+tuple(_info.keys()))
           spec_length = spec.spectrum_length
           # 'array' in str(type(i)) and
           # _arrays = {k : val for k,val in _arrays.items() if len(val) == spec_length}
           _spec_array_sliced = {k : val[ind] for k,val in _arrays.items() if len(val) == spec_length}
           # array_test = [(i,getattr(spec,i)) for i in spec._fields if len(getattr(spec,i)) == spec_length]
           # array_cols = [i[0] for i in array_test] # arrays = [i[1] for i in array_test]
           # spec_info = dict([(i,getattr(spec,i)) for i in spec._fields if i not in array_cols])
           # spec_array_sliced = dict([(i[0],i[1][ind]) for i in array_test])
           SpecSlice = SpecSlice_template(**{**_info,**_spec_array_sliced, **{'windowname' : windowname}})
           return SpecSlice
           
       
       def clean_spec_cols():
           return ('Zt', 'Zt_threshold','int_despike','int_filter_despike')
       
       