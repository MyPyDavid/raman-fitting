#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from collections import namedtuple


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
           
           SpecSlice_template = namedtuple('SpectrumSliced',spec._fields+('windowname',))
           spec_length = spec.spectrum_length
           array_test = [(n,i) for n,i in zip(spec._fields,spec) if 'array' in str(type(i)) and len(i) == spec_length]
           array_cols = [i[0] for i in array_test] # arrays = [i[1] for i in array_test]
           spec_info = dict([(i,getattr(spec,i)) for i in spec._fields if i not in array_cols])
           spec_array_sliced = dict([(i[0],i[1][ind]) for i in array_test])
           SpecSlice = SpecSlice_template(**{**spec_info,**spec_array_sliced, **{'windowname' : windowname}})
           return SpecSlice
           
       
       def clean_spec_cols():
           return ('Zt', 'Zt_threshold','int_despike','int_filter_despike')
       
       def check_input_return_intensity(test):
           type_test = str(type(test))
           if '__main__' in type_test:
               if 'intensity' in test._fields:
                   int_used = test.intensity
           elif 'numpy.ndarray' in type_test:
               int_used = test
           elif 'dict' in type_test:
               int_used = test.get([i for i in test.keys() if 'intensity' in i][0])
   #             = test
           else:
               print(f'Despike input error {type_test}')
               int_used = test
           return int_used