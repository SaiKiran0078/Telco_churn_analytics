"""Power BI project checks (no Power BI Desktop needed) and parity between the report's logic and the Python results."""
import os, subprocess, sys, unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
EXPR = PBI / "Telco Churn Report.SemanticModel" / "definition" / "expressions.tmdl"


def run(*args):
    return subprocess.run([sys.executable, "-I", *map(str, args)], capture_output=True, text=True)


class TestProjectFiles(unittest.TestCase):
    def test_field_references_resolve(self):
        r = run(ROOT / "scripts" / "check_refs.py", PBI)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK: all references resolve", r.stdout)

    @unittest.skipUnless(os.environ.get("MS_SCHEMAS"), "set MS_SCHEMAS to a clone of github.com/microsoft/json-schemas")
    def test_schema_validation(self):
        r = run(ROOT / "scripts" / "validate_pbip.py", PBI, os.environ["MS_SCHEMAS"])
        self.assertIn("invalid: 0", r.stdout, r.stdout + r.stderr)

    def test_placeholder_path_is_committed(self):
        self.assertIn('expression RepoRoot = "C:\\telco-churn-analytics"', EXPR.read_text(encoding="utf-8"),
                      "run: python scripts/init.py --reset")

    def test_init_roundtrip(self):
        before = EXPR.read_bytes()
        try:
            self.assertEqual(run(ROOT / "scripts" / "init.py").returncode, 0)
            self.assertIn(str(ROOT), EXPR.read_text(encoding="utf-8"))
        finally:
            EXPR.write_bytes(before)
        self.assertEqual(EXPR.read_bytes(), before)

    def test_five_pages(self):
        pages = list((PBI / "Telco Churn Report.Report" / "definition" / "pages").glob("*/page.json"))
        self.assertEqual(len(pages), 5)


def load_like_powerbi():
    """Re-implements the Power Query steps of the Customers table in pandas."""
    r = pd.read_csv(ROOT / "data" / "raw" / "Telco-Customer-Churn.csv", dtype=str)
    r["TotalCharges"] = pd.to_numeric(r.TotalCharges.str.strip().replace("", "0"))
    r["MonthlyCharges"] = pd.to_numeric(r.MonthlyCharges); r["tenure"] = r.tenure.astype(int)
    r["SeniorCitizen"] = np.where(r.SeniorCitizen == "1", "Yes", "No")
    svc = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
    r[svc] = r[svc].replace("No internet service", "No")
    r["MultipleLines"] = r.MultipleLines.replace("No phone service", "No")
    r["PaymentMethod"] = r.PaymentMethod.str.replace(" (automatic)", "", regex=False)
    r["cf"] = (r.Churn == "Yes").astype(int)
    r["num_services"] = (r[svc] == "Yes").sum(axis=1) + (r.PhoneService == "Yes") + (r.InternetService != "No")
    scores = pd.read_csv(ROOT / "reports" / "tables" / "customer_risk_scores.csv")
    return r.merge(scores[["customerID", "segment", "churn_probability", "risk_tier"]], on="customerID", how="left")


class TestLogicParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = load_like_powerbi()

    def test_same_cleaning_as_python_pipeline(self):
        clean = pd.read_csv(ROOT / "data" / "processed" / "telco_clean.csv")
        pd.testing.assert_series_equal(self.d.cf, clean.ChurnFlag, check_names=False)
        pd.testing.assert_series_equal(self.d.TotalCharges, clean.TotalCharges, check_names=False)
        self.assertTrue((self.d.PaymentMethod == clean.PaymentMethod).all())
        self.assertTrue((self.d.MultipleLines == clean.MultipleLines).all())

    def test_every_customer_has_a_score(self):
        self.assertEqual(self.d.churn_probability.isna().sum(), 0)

    def test_headline_kpis(self):
        d = self.d
        self.assertEqual(len(d), 7043); self.assertEqual(d.cf.sum(), 1869)
        self.assertEqual(round(d.cf.mean() * 100, 1), 26.5)
        self.assertEqual(round(d.MonthlyCharges.sum()), 456117)
        self.assertEqual(round(d[d.cf == 1].MonthlyCharges.sum()), 139131)

    def test_insight_figures(self):
        d = self.d; m2m = d.Contract == "Month-to-month"
        self.assertEqual(round(m2m.mean() * 100), 55)
        self.assertEqual(round(d[m2m].cf.sum() / d.cf.sum() * 100, 1), 88.6)
        net = d[d.InternetService != "No"]
        prot = (net[["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport"]] == "Yes").sum(axis=1)
        self.assertEqual(round(net[prot == 0].cf.mean() * 100, 1), 56.7)
        self.assertEqual(round(net[prot == 4].cf.mean() * 100, 1), 5.3)

    def test_call_list_and_simulator_defaults(self):
        d = self.d
        call = d[(d.cf == 0) & (d.risk_tier == "High")]
        self.assertEqual(len(call), 534)
        sel = d[d.churn_probability >= 0.27]
        gain = sel[sel.cf == 1].MonthlyCharges.sum() * 0.30 * 12; cost = 50 * len(sel)
        self.assertEqual(len(sel), 2872); self.assertEqual(round(gain - cost), 270221)
        be = cost / (sel[sel.cf == 1].MonthlyCharges.sum() * 12)
        self.assertEqual(round(be * 100, 1), 10.4)  # matches the break-even in PROJECT_REPORT.md


if __name__ == "__main__":
    unittest.main()
