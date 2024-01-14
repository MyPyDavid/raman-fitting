import unittest


from raman_fitting.models.deconvolution.init_models import InitializeModels
from raman_fitting.delegating.main_delegator import (
    MainDelegator,
    add_make_sample_group_destdirs,
)


class TestMainDelegator(unittest.TestCase):
    def setUp(self):
        self.maindebug = MainDelegator(run_mode="debug")

    def test_initialize_models(self):
        self.assertTrue(isinstance(self.maindebug.models, InitializeModels))

    def test_index(self):
        self.assertTrue(hasattr(self.maindebug, "index"))
        self.assertTrue(isinstance(getattr(self.maindebug, "index"), list))

        sample_group = self.maindebug.sample_group_gen(self.maindebug.index)
        grp_name, grp_files = next(sample_group)
        if 0:
            group_files = list(grp_files)
            destdirs = add_make_sample_group_destdirs(group_files)
            destdirs_str = [i for i in destdirs.values if isinstance(i, str)]
            alltest = all([grp_name in i for i in destdirs_str])
            self.assertTrue(alltest)

    def test_generator(self):
        _sample_group = self.maindebug.sample_group_gen(self.maindebug.index)
        grp_name, sgrp_grpr = next(_sample_group)
        self.assertTrue(grp_name)

        # breakpoint()
        _sID_gen = self.maindebug.sample_id_gen(sgrp_grpr)
        sID_name, sample_grpr = next(_sID_gen)
        self.assertTrue(sID_name)


if __name__ == "__main__":
    unittest.main()
    self = TestMainDelegator()
