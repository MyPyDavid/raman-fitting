import unittest

from raman_fitting.utils.coordinators import FieldsTracker, FieldsTrackerWarning


class TestFieldsTracker(unittest.TestCase):
    def testFCO(self):

        #%%
        fco = FieldsTracker(
            fields=["peak_name", "peak_type", "param_hints"],
            sources=("kwargs", "cls_dict", "init"),
        )
        assert not fco.results
        assert fco.status == False

        fco.store("kwargs", "peak_name", "R2D2")

        with self.assertWarns(UserWarning) as cm:
            fco.store("cls_dict", "peak_name", "R4D4")
        self.assertIn(
            "Field peak_name has multiple sources", ", ".join(map(str, cm.warning.args))
        )

        with self.assertWarns(UserWarning) as cm:
            fco.store("notinsources", "peak_name", "R4D4")
        self.assertIn(
            "Store in notinsources at peak_name", ", ".join(map(str, cm.warning.args))
        )

        fco.store("init", "peak_type", "Voirentzian")

        with self.assertWarns(UserWarning) as cm:
            fco.store("init", "peak_type", "Voirentzian")
        self.assertIn(
            "Redefinition of peak_type in init ignored",
            ", ".join(map(str, cm.warning.args)),
        )

        fco.store("init", "peak_name", "Voirentzian")
        fco.store("init", "param_hints", "Voirentzian")
        fco.store("init", "peak_type", "Voirentzian")

        assert set(fco.results.keys()) == set(["peak_name", "peak_type", "param_hints"])
        assert fco.status == True

        _test_dict = {
            "peak_name": "multi_store",
            "peak_type": "multi_test",
            "param_hints": 2,
        }
        fco.multi_store("cls_dict", **_test_dict)
        assert fco.register["cls_dict"] == _test_dict
        assert fco.results["param_hints"]["value"] == 2
