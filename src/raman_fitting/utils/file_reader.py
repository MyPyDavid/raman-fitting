""" Class for reading in files, can be extended for other than txt formats"""

from pathlib import Path

import numpy as np


class FileReader:
    def __init__(self, file_path=Path()):
        self._file_path = file_path
        self.read_in()

    def read_in(self):
        ramanshift, intensity_raw = np.array([]), np.array([])
        i = 0
        while not ramanshift.any():
            try:
                ramanshift, intensity_raw = np.loadtxt(
                    self._filepath, usecols=(0, 1), unpack=True, skiprows=i
                )
                print(self._filepath, len(ramanshift), len(intensity_raw))
                self._skiprows = i
                self._read_succes = True
            except ValueError:
                i += 1

        self.ramanshift = ramanshift
        self.intensity_raw = intensity_raw
