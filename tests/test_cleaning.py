import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from churn.data import clean, load_raw, quality_report  # noqa: E402
from churn.features import add_features  # noqa: E402


class TestCleaning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = load_raw()
        cls.df, cls.log = clean(cls.raw)

    def test_row_count_preserved(self):
        self.assertEqual(len(self.df), len(self.raw))

    def test_total_charges_numeric_and_complete(self):
        self.assertTrue(pd.api.types.is_float_dtype(self.df["TotalCharges"]))
        self.assertEqual(int(self.df["TotalCharges"].isna().sum()), 0)

    def test_zero_tenure_customers_have_zero_total(self):
        z = self.df[self.df["tenure"] == 0]
        self.assertGreater(len(z), 0)
        self.assertTrue((z["TotalCharges"] == 0).all())

    def test_no_service_labels_removed(self):
        for c in ["OnlineSecurity", "MultipleLines", "StreamingTV"]:
            self.assertEqual(set(self.df[c].unique()), {"Yes", "No"})

    def test_target_matches_label(self):
        self.assertTrue(((self.df["Churn"] == "Yes") == (self.df["ChurnFlag"] == 1)).all())

    def test_quality_report_keys(self):
        q = quality_report(self.raw)
        self.assertEqual(q["total_charges_not_numeric"], 11)

    def test_features_have_no_label_leakage(self):
        f = add_features(self.df)
        self.assertTrue(f["NumServices"].between(0, 8).all())
        # derived features must not depend on the label: rebuilding them with the label scrambled changes nothing
        scrambled = self.df.assign(ChurnFlag=self.df["ChurnFlag"].sample(frac=1, random_state=0).values)
        g = add_features(scrambled)
        for c in ["NumServices", "ChargesPerService", "AvgMonthlySpend", "ChargeVsExpected"]:
            self.assertTrue((f[c] == g[c]).all())


if __name__ == "__main__":
    unittest.main()
