import logging
import unittest


from raman_fitting.deconvolution_models.base_peak import (
    BasePeak,
)


logger = logging.getLogger(__name__)
logging.captureWarnings(True)  # sends these warning to the logger


def _error_message_contains(excinfo, testmsg: str, verbose: bool = False):
    _fltr_str = [
        i if i not in ["(", ")"] else " "
        for i in str(excinfo.value)
        if i.isalnum() or i in (",", ".", " ", "_", "(", ")")
    ]
    _cl_str = "".join(map(str, _fltr_str))
    _cl_str_split = _cl_str.split(" ")
    _test = all(i in _cl_str_split for i in testmsg.split(" "))

    if not _test:
        _test = any(i in _cl_str_split for i in testmsg.split(" "))

    if not _test or verbose:
        print(list(((i, i in _cl_str_split) for i in testmsg.split(" "))))
        print(_cl_str_split)
    return _test


class TestBasePeak(unittest.TestCase):
    def test_basepeak_initialization(self):
        # self.assertRaises(ValidationError, BasePeak())
        # self.assertRaises(ValidationError, BasePeak(), peak_name="test")
        # self.assertRaises(ValidationError, BasePeak(), peak_type="Voigt")

        test_peak = BasePeak(peak_name="test", peak_type="Voigt")
        assert test_peak.peak_name == "test"

    @unittest.skip("TODO: add field validations")
    def test_empty_base_class_with_kwargs_raises(self):
        eb = BasePeak(peak_type="Voigt", peak_name="test")

        self.assertEqual(eb.peak_type, "Voigt")

        # TODO built in field validation str_length
        # with pytest.raises(ValueError) as excinfo:
        #     eb.peak_name = 10 * "emptytest"
        # self.assertTrue(
        #     _error_message_contains(excinfo, "value for peak_name is too long 90")
        # )

        # TODO built in field validation for peak_type
        # with pytest.raises(ValueError) as excinfo:
        #     eb.peak_type = "VoigtLorentzian"
        # self.assertTrue(
        #     _error_message_contains(
        #         excinfo,
        #         ''''Multiple options ['Lorentzian', 'Voigt'] for misspelled value "VoigtLorentzian"''',
        #     )
        # )

    def test_base_class_good_with_init_extra_tests(self):
        td1_kwargs = dict(
            peak_type="Voigt",
            peak_name="D1D1",
            param_hints={
                "center": {"value": 2650, "min": 2600, "max": 2750},
                "sigma": {"value": 60, "min": 1, "max": 200},
                "amplitude": {"value": 14, "min": 1e-03, "max": 100},
            },
        )

        td1 = BasePeak(**td1_kwargs)
        self.assertEqual(td1.peak_type, "Voigt")
        self.assertEqual(td1.peak_name, "D1D1")
        peakmod = "<lmfit.Model: Model(voigt, prefix='D1D1_')>"
        self.assertEqual(str(td1.lmfit_model), peakmod)
        # _class_str = f"center : 2600 < 2650 > 2750"
        # self.assertIn(_class_str, str(td1))
        # dont test attr setters
        # td1.peak_name = "R2D2"
        # self.assertEqual(td1.lmfit_model.prefix, "R2D2_")

    def test_base_class_good_with_init(self):
        d1_kwargs = dict(
            peak_name="D1D1",
            peak_type="Gaussian",
            param_hints={
                "center": {"value": 2650, "min": 2600, "max": 2750},
                "sigma": {"value": 60, "min": 1, "max": 200},
                "amplitude": {"value": 14, "min": 1e-03, "max": 100},
            },
        )

        td1 = BasePeak(**d1_kwargs)
        self.assertEqual(td1.peak_name, d1_kwargs["peak_name"])

    def test_base_class_good_with_init_added_method(self):
        tkwargs = dict(
            peak_type="Lorentzian",
            peak_name="D1D1",
            param_hints={
                "center": {"value": 2650, "min": 2600, "max": 2750},
                "sigma": {"value": 60, "min": 1, "max": 200},
                "amplitude": {"value": 14, "min": 1e-03, "max": 100},
            },
        )

        td1m = BasePeak(**tkwargs)
        # breakpoint()
        self.assertEqual(td1m.peak_type, tkwargs["peak_type"])
        self.assertEqual(td1m.peak_name, tkwargs["peak_name"])

    def test_base_class_good_with_attributes_and_init(self):
        tkwargs = dict(
            param_hints={
                "center": {"value": 2435, "min": 2400, "max": 2550},
                "sigma": {"value": 30, "min": 1, "max": 200},
                "amplitude": {"value": 2, "min": 1e-03, "max": 100},
            },
            peak_type="Voigt",
            peak_name="R2D2",
        )

        nca = BasePeak(**tkwargs)
        _center_value = nca.lmfit_model.param_hints["center"]["value"]
        assert _center_value == 2435

    def test_base_class_good_with_attributes_no_init(self):
        tkwargs = dict(
            param_hints={
                "center": {"value": 2435, "min": 2400, "max": 2550},
                "sigma": {"value": 30, "min": 1, "max": 200},
                "amplitude": {"value": 2, "min": 1e-03, "max": 100},
            },
            peak_type="Voigt",
            peak_name="R2D2",
        )

        ncni = BasePeak(**tkwargs)
        # breakpoint()
        # _center_value =
        assert ncni.param_hints["center"].value == 2435
        assert ncni.lmfit_model.param_hints["center"]["value"] == 2435

    def test_base_class_good_with_attributes_init_collision_values(self):
        tkwargs = dict(
            param_hints={
                "center": {"value": 2435, "min": 2400, "max": 2550},
                "sigma": {"value": 30, "min": 1, "max": 200},
                "amplitude": {"value": 2, "min": 1e-03, "max": 100},
            },
            peak_type="Voigt",
            peak_name="R2D2",
        )
        nci = BasePeak(**tkwargs)
        self.assertEqual(nci.peak_type, "Voigt")
        self.assertEqual(nci.lmfit_model.param_hints["center"]["value"], 2435)

    # def test_base_with_only_keyword_args(self):
    #     new = BasePeak("newPeak", **{"noname": 2, "debug": False, "peak_type": "Voigt"})
    #     new.param_hints = {"center": {"value": 200}}
    #     newinst = new()
    # _newinst_str = "newPeak, <lmfit.Model: Model(voigt, prefix='newPeak_')>, center : -inf < 200 > inf"
    # self.assertEqual(str(newinst), _newinst_str)


# %%
if __name__ == "__main__":
    unittest.main()
    self = TestBasePeak()
