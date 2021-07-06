import datetime
import unittest

# from raman_fitting.deconvolution_models import first_order_peaks
import pandas as pd
import pytest

import raman_fitting
from raman_fitting.datafiles import example_files
from raman_fitting.deconvolution_models.base_model import InitializeModels
from raman_fitting.delegator.main_delegator import (
    MainDelegator,
    add_make_sample_group_destdirs,
)


class TestMainDelegator(unittest.TestCase):
    def setUp(self):
        self.maindebug = MainDelegator(run_mode="DEBUG")
        self.models = self.maindebug.initialize_models()

    def test_initialize_models(self):
        self.assertTrue(isinstance(self.models, InitializeModels))

    def test_index(self):
        self.assertTrue(hasattr(self.maindebug, "index"))
        self.assertTrue(isinstance(getattr(self.maindebug, "index"), pd.DataFrame))

        _sample_group = self.maindebug.sample_group_gen()
        _arg = next(_sample_group)
        _destdirs = add_make_sample_group_destdirs(_arg[-1])
        _alltest = all([_arg[0] in a for a in [i.parts for i in _destdirs.values()]])
        self.assertTrue(_alltest)

    def test_generator(self):

        _sample_group = self.maindebug.sample_group_gen()
        _sample_group_arg = next(_sample_group)
        self.assertTrue(_sample_group_arg)

        _sID_gen = self.maindebug._sID_gen(*_sample_group_arg)
        _sID_arg = next(_sID_gen)
        self.assertTrue(_sID_arg)

        # while True:

        #     try:

        #     except StopIteration as e:
        #         print(e)


if __name__ == "__main__":
    unittest.main()
    self = TestMainDelegator()
