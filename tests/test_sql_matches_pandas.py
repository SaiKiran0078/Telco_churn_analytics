"""The SQL answers must agree with the pandas answers (two independent routes to the same numbers)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]

import pandas as pd  # noqa: E402

from churn.config import CLEAN  # noqa: E402
import run_sql  # noqa: E402


class TestSqlAgreesWithPandas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(CLEAN)
        cls.res = run_sql.run(verbose=False)

    def test_kpis(self):
        k = self.res["01_headline_kpis"].iloc[0]
        self.assertEqual(int(k.customers), len(self.df))
        self.assertEqual(int(k.churned), int(self.df.ChurnFlag.sum()))
        self.assertAlmostEqual(k.churn_rate_pct, round(self.df.ChurnFlag.mean() * 100, 1))
        self.assertAlmostEqual(k.mrr_lost, round(self.df.loc[self.df.ChurnFlag == 1, "MonthlyCharges"].sum()), delta=1)

    def test_churn_by_contract(self):
        t = self.res["02_churn_by_contract"].set_index("Contract")
        exp = (self.df.groupby("Contract").ChurnFlag.mean() * 100).round(1)
        for c in exp.index:
            self.assertAlmostEqual(t.loc[c, "churn_rate_pct"], exp[c])

    def test_highest_risk_group(self):
        d = self.df
        g = d[(d.Contract == "Month-to-month") & (d.InternetService == "Fiber optic") & (d.TechSupport == "No") & (d.OnlineSecurity == "No")]
        r = self.res["06_highest_risk_group"].iloc[0]
        self.assertEqual(int(r.customers), len(g))
        self.assertAlmostEqual(r.churn_rate_pct, round(g.ChurnFlag.mean() * 100, 1))


if __name__ == "__main__":
    unittest.main()
