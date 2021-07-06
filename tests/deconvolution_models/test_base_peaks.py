import copy
import unittest

import pytest
from lmfit import Model

# from raman_fitting.deconvolution_models import first_order_peaks
import raman_fitting
from raman_fitting.deconvolution_models.default_peaks.base_peak import (
    BasePeak,
    BasePeakWarning,
    LMfitModelConstructorMethods,
)

#%%


def _error_message_contains(excinfo, testmsg: str, verbose: bool = False):
    _fltr_str = [
        i if not i in ["(", ")"] else " "
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


#%%


class TestBasePeak(unittest.TestCase):

    #%% TESTING

    def test_BasePeak_attributes(self):
        self.assertTrue(BasePeak.__doc__)
        self.assertTrue(BasePeak._fields)
        self.assertTrue(BasePeak._sources)
        self.assertTrue(BasePeak.PEAK_TYPE_OPTIONS)

    def test_empty_base_class_raises(self):
        #%%

        class EmptyTestChild(metaclass=BasePeak):
            pass

        eb = EmptyTestChild()

        with pytest.raises(ValueError) as excinfo:
            eb.peak_type = "emptytest"
        assert _error_message_contains(excinfo, "value emptytest for peak_type not in")

        with pytest.raises(ValueError) as excinfo:
            eb.peak_name = 10 * "emptytest"
        assert _error_message_contains(excinfo, "value for peak_name is too long 90")

        self.assertFalse(eb.peak_model)

        #%%

    def test_empty_base_class_with_kwargs_raises(self):
        #%%

        class EmptyTestChild(
            metaclass=BasePeak,
            testkwarg2=2,
            testkwarg3=3,
            peak_type="Voigt",
            verbose=True,
        ):
            pass

        eb = EmptyTestChild()
        #%%

        self.assertEqual(eb.peak_type, "Voigt")
        self.assertEqual(eb.testkwarg2, 2)

        with pytest.raises(ValueError) as excinfo:
            eb.peak_type = "emptytest"
        self.assertTrue(
            _error_message_contains(excinfo, "value emptytest for peak_type not in")
        )

        with pytest.raises(ValueError) as excinfo:
            eb.peak_name = 10 * "emptytest"
        self.assertTrue(
            _error_message_contains(excinfo, "value for peak_name is too long 90")
        )

        self.assertFalse(eb.peak_model)
        # with pytest.raises(AttributeError) as excinfo:
        #     eb.peak_model
        # self.assertTrue(
        #     _error_message_contains(
        #         excinfo, "type object empty no attribute _peak_model"
        #     )
        # )

        with pytest.raises(ValueError) as excinfo:
            eb.peak_type = "VoigtLorentzian"
        self.assertTrue(
            _error_message_contains(
                excinfo,
                ''''Multiple options ['Lorentzian', 'Voigt'] for misspelled value "VoigtLorentzian"''',
            )
        )

    def test_empty_base_class_with_false_input(self):
        #%%

        class EmptyTestChild(metaclass=BasePeak, peak_type="FalsePeak"):
            pass

        with pytest.raises(ValueError) as excinfo:
            eb = EmptyTestChild()
        self.assertTrue(
            _error_message_contains(excinfo, "value emptytest for peak_type not in")
        )

    #%%
    def test_base_class_good_with_init_extra_tests(self):
        #%%
        class TestD1peak(metaclass=BasePeak, debug=True):
            """
            here is docstring of TestD1peak,
            small spelling error on peak_type
            """

            def __init__(self, *args, **kwargs):
                print(f"called __init__ {self} TestD1peak, with {args}, {kwargs}")
                self._peak_type = "Voigt"
                self.peak_name = "D1D1"
                self.input_param_settings = {
                    "center": {"value": 2650, "min": 2600, "max": 2750},
                    "sigma": {"value": 60, "min": 1, "max": 200},
                    "amplitude": {"value": 14, "min": 1e-03, "max": 100},
                }

        td1 = TestD1peak()
        peakmod = "<lmfit.Model: Model(voigt, prefix='D1D1_')>"
        self.assertEqual(str(td1.peak_model), peakmod)
        _class_str = f"TestD1peak, {peakmod}, center : 2600 < 2650 > 2750"
        self.assertIn(_class_str, str(td1))
        td1.peak_name = "R2D2"
        self.assertEqual(td1.peak_model.prefix, "R2D2_")

        # _def_param = td1.param_hints_constructor({})
        # _def_key = list(BasePeak.default_settings.keys())[0]
        # _def_param[_def_key].value == BasePeak.default_settings[_def_key]["value"]

        # _def_param = td1.param_hints_constructor(
        #     td1.fco.register["init"]["param_hints"]
        # )
        # self.assertEqual(_def_param["amplitude"].value, 14)

        # with pytest.raises(TypeError) as excinfo:
        #     _def_param = td1.param_hints_constructor("fail")
        # self.assertTrue(
        #     _error_message_contains(
        #         excinfo,
        #         "input_param_hints should be of type dictionary not <class 'str'>",
        #     )
        # )

        # _err_hints = copy.copy(td1.fco.register["init"]["param_hints"])
        # _err_hints["center"] = (1, 2, 3, 4)

        # with pytest.raises(ValueError) as excinfo:
        #     _def_param = td1.param_hints_constructor(_err_hints)
        # self.assertTrue(
        #     _error_message_contains(
        #         excinfo, " Unable to create a Parameter from center and (1, 2, 3, 4):"
        #     )
        # )

    #%%
    def test_base_class_good_with_init(self):
        class TestD1peak(metaclass=BasePeak, debug=True):
            """
            test_base_class_good_with_init
            but with spelling error in peak_type
            """

            def __init__(self, *args, **kwargs):
                print(f"called __init__ {self} TestD1peak, with {args}, {kwargs}")
                self._peak_type = "cartVoigt"
                self.peak_name = "D1D1"
                self.input_param_settings = {
                    "center": {"value": 2650, "min": 2600, "max": 2750},
                    "sigma": {"value": 60, "min": 1, "max": 200},
                    "amplitude": {"value": 14, "min": 1e-03, "max": 100},
                }

        td1 = TestD1peak()
        _class_str = "TestD1peak, <lmfit.Model: Model(voigt, prefix='D1D1_')>, center : 2600 < 2650 > 2750"
        self.assertIn(_class_str, str(td1))
        # print(td1)

    #%%

    def test_base_class_good_with_init_added_method(self):
        #%%
        class TestD1peakmeta(metaclass=BasePeak, a=2):
            """
            here is docstring of TestD1peak
            """

            def __init__(self, *args, **kwargs):
                # super().__init__(self)
                # print(f'__subclass __init__ self "{self}" TestD1peakmeta, with {args}, {kwargs}')
                self.peak_type = "Lorentzian"
                self.peak_name = "D1D1"
                self.input_param_settings = {
                    "center": {"value": 2650, "min": 2600, "max": 2750},
                    "sigma": {"value": 60, "min": 1, "max": 200},
                    "amplitude": {"value": 14, "min": 1e-03, "max": 100},
                }
                self._meta_added_method(kwargs)

            def _meta_added_method(self, *args, **kwargs):
                """added method"""
                print(f"{self.__dict__}")
                self._added_method_arg = kwargs
                print(f"added method called {kwargs}")
                # return arg

        td1m = TestD1peakmeta(add=33)
        _teststr = "TestD1peakmeta, <lmfit.Model: Model(lorentzian, prefix='D1D1_')>, center : 2600 < 2650 > 2750"
        self.assertIn(_teststr, str(td1m))
        # assert str(td1m) == _teststr

        #%%

    def test_base_class_good_with_attributes_and_init(self):
        #%%
        class NewChildClassAttr(metaclass=BasePeak):
            """New child class for easier definition"""

            _test = "testkwarg"

            param_hints = {
                "center": {"value": 2435, "min": 2400, "max": 2550},
                "sigma": {"value": 30, "min": 1, "max": 200},
                "amplitude": {"value": 2, "min": 1e-03, "max": 100},
            }
            peak_type = "Voigt"  #'Voigt'
            peak_name = "R2D2"

            def __init__(self, **kwargs):
                # print(f'__init child empty pass {self}')
                pass
                # super().__init__()

        nca = NewChildClassAttr()
        _center_value = nca.peak_model.param_hints["center"]["value"]
        assert _center_value == 2435
        # print('Instance child:', nca)
        #%%

    def test_base_class_good_with_attributes_no_init(self):
        class NewChildClassAttrNoInit(metaclass=BasePeak):
            """New child class for easier definition"""

            _test = "testkwarg"

            param_hints = {
                "center": {"value": 2435, "min": 2400, "max": 2550},
                "sigma": {"value": 30, "min": 1, "max": 200},
                "amplitude": {"value": 2, "min": 1e-03, "max": 100},
            }
            peak_type = "Voigt"  #'Voigt'
            peak_name = "R2D2"
            # def __init__(self,**kwargs):
            # print(f'__init child empty pass {self}')
            # pass
            # super().__init__()

        ncni = NewChildClassAttrNoInit()
        _center_value = ncni.peak_model.param_hints["center"]["value"]
        assert _center_value == 2435

        #%%

    def test_base_class_good_with_attributes_init_collision_values(self):
        #%%
        class NewChildClassInit(metaclass=BasePeak, peak_type="Gaussian"):
            """New child class for easier definition"""

            _test = "testkwarg"
            peak_type = "Lorentzian"
            param_hints = {
                "center": {"value": 2435, "min": 2400, "max": 2550},
                "sigma": {"value": 30, "min": 1, "max": 200},
                "amplitude": {"value": 2, "min": 1e-03, "max": 100},
            }

            def __init__(self, **kwargs):
                self.peak_type = "Voigt"
                self.peak_name = "R2D2"
                self.param_hints = {"center": {"value": 20}}

                # self.param_hints = {
                #                     'center':
                #                         {'value': 2435,'min': 2400, 'max': 2550},
                #                     'sigma':
                #                         {'value': 30,'min' : 1, 'max': 200},
                #                     'amplitude' :
                #                         {'value': 2,'min' : 1E-03, 'max': 100}
                #                         }
                # super().__init__(self)

        nci = NewChildClassInit()
        self.assertEqual(nci.peak_type, "Gaussian")
        self.assertEqual(nci.peak_model.param_hints["center"]["value"], 2435)
        # print(nci)
        # print(self.__dict__)

    def test_base_with_only_keyword_args(self):
        new = BasePeak("newPeak", **{"noname": 2, "debug": False, "peak_type": "Voigt"})
        new.param_hints = {"center": {"value": 200}}
        newinst = new()
        _newinst_str = "newPeak, <lmfit.Model: Model(voigt, prefix='newPeak_')>, center : -inf < 200 > inf"
        self.assertEqual(str(newinst), _newinst_str)


class TestLMfitModelConstructorMethods(unittest.TestCase):

    LMfit = LMfitModelConstructorMethods

    def test_make_model_from_peak_type_and_name(self):

        model = self.LMfit.make_model_from_peak_type_and_name(
            peak_type="Voigt", peak_name="lmfitpeak"
        )
        self.assertTrue(isinstance(model, Model))
        self.assertEqual(model.prefix, "lmfitpeak")

        with pytest.raises(NotImplementedError) as excinfo:
            model = self.LMfit.make_model_from_peak_type_and_name(peak_type="FalsePeak")
        self.assertTrue(
            _error_message_contains(
                excinfo,
                " This peak type or model 'FalsePeak' has not been implemented.",
            )
        )


# self = TestLMfitModelConstructorMethods()


#%%
if __name__ == "__main__":
    unittest.main()
    self = TestBasePeak()
