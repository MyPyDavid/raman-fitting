import unittest


from raman_fitting.delegating.main_delegator import (
    MainDelegator,
    add_make_sample_group_destdirs,
)


class TestMainDelegator(unittest.TestCase):
    def setUp(self):
        self.delegator = MainDelegator(run_mode="debug")

    def test_initialize_models(self):
        self.assertIn("first_order", self.delegator.lmfit_models)
        self.assertIn("first_order", self.delegator.selected_models)
        self.assertRaises(
            self.delegator.select_fitting_model("no_name", "not"), ValueError
        )

    def test_index(self):
        # breakpoint()
        # index = self.delegator.select_samples_from_index()
        self.assertTrue(hasattr(self.delegator, "index"))
        self.assertEqual(len(self.delegator.index.raman_files), 5)
        selection = self.delegator.select_samples_from_index()
        self.assertEqual(len(self.delegator.index.raman_files), len(selection))

    @unittest.skip("enable main_run before release.")
    def test_main_run(self):
        self.delegator.main_run()
        self.assertTrue(self.delegator.results)

    def _test_delegator(self):
        sample_group = self.delegator.sample_group_gen(self.delegator.index)
        grp_name, grp_files = next(sample_group)
        if 0:
            group_files = list(grp_files)
            destdirs = add_make_sample_group_destdirs(group_files)
            destdirs_str = [i for i in destdirs.values if isinstance(i, str)]
            alltest = all([grp_name in i for i in destdirs_str])
            self.assertTrue(alltest)

    def _test_generator(self):
        _sample_group = self.delegator.sample_group_gen(self.delegator.index)
        grp_name, sgrp_grpr = next(_sample_group)
        self.assertTrue(grp_name)

        # breakpoint()
        _sID_gen = self.delegator.sample_id_gen(sgrp_grpr)
        sID_name, sample_grpr = next(_sID_gen)
        self.assertTrue(sID_name)


if __name__ == "__main__":
    unittest.main()
    self = TestMainDelegator()
