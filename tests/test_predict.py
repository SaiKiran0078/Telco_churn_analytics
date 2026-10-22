import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from churn.config import RAW  # noqa: E402
from churn.predict import score_frame  # noqa: E402


class TestPredict(unittest.TestCase):
    def test_scores_raw_file_without_target(self):
        raw = pd.read_csv(RAW).drop(columns=["Churn"]).head(200)
        out = score_frame(raw)
        self.assertEqual(len(out), 200)
        self.assertTrue(out.churn_probability.between(0, 1).all())
        self.assertEqual(set(out.risk_tier.astype(str)) <= {"Low", "Medium", "High"}, True)

    def test_month_to_month_new_customer_riskier_than_long_two_year(self):
        raw = pd.read_csv(RAW)
        a = raw[(raw.Contract == "Month-to-month") & (raw.tenure <= 2) & (raw.InternetService == "Fiber optic")].head(30)
        b = raw[(raw.Contract == "Two year") & (raw.tenure >= 60)].head(30)
        pa, pb = score_frame(a).churn_probability.mean(), score_frame(b).churn_probability.mean()
        self.assertGreater(pa, pb + 0.3)


if __name__ == "__main__":
    unittest.main()
