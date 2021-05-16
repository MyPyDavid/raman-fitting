#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  1 14:37:37 2021

@author: zmg
"""


class FileReader():
    
    
    def __init__(self,file_path = Path()):
        self._file_path = file_path
        self.read_in()
        
    def read_in(self):
        ramanshift, intensity_raw= np.array([]),np.array([])
        i = 0
        while not ramanshift.any():
            try:
                ramanshift, intensity_raw = np.loadtxt(self._filepath, usecols=(0, 1), unpack=True, skiprows=i)
                print(self._filepath, len(ramanshift),len(intensity_raw))
                self._skiprows = i
                self._read_succes = True
            except ValueError:
                i += 1
        
        self.ramanshift = ramanshift
        self.intensity_raw = intensity_raw
        
    
    