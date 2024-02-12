import unittest


from raman_fitting.delegating.main_delegator import MainDelegator


class TestMainDelegator(unittest.TestCase):
    def setUp(self):
        self.delegator = MainDelegator(run_mode="pytest")

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


if __name__ == "__main__":
    unittest.main()
    self = TestMainDelegator()
