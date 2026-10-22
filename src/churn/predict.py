"""Score new customers with the saved model.

    PYTHONPATH=src python -m churn.predict --input data/raw/Telco-Customer-Churn.csv --output scored.csv

The input must have the same columns as the raw Telco file (the Churn column is optional). The same cleaning
and feature steps used in training are applied, so raw exports can be scored directly.
"""
import argparse
import json

import joblib
import pandas as pd

from .config import FIG, MODELS
from .data import clean
from .features import add_features
from .modeling import FEATURES


def score_frame(raw: pd.DataFrame) -> pd.DataFrame:
    raw = raw.copy()
    if "Churn" not in raw.columns:
        raw["Churn"] = "No"  # placeholder so the shared cleaning code runs; it is never used for scoring
    df, _ = clean(raw)
    df = add_features(df)
    model = joblib.load(MODELS / "churn_model.joblib")
    with open(FIG.parent / "metrics.json", encoding="utf-8") as f:
        thr = json.load(f)["threshold"]
    p = model.predict_proba(df[FEATURES])[:, 1]
    out = df[["customerID", "Contract", "tenure", "MonthlyCharges"]].copy()
    out["churn_probability"] = p.round(4)
    out["risk_tier"] = pd.cut(p, [-0.01, thr, 0.5, 1.0], labels=["Low", "Medium", "High"])
    return out.sort_values("churn_probability", ascending=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    out = score_frame(pd.read_csv(a.input))
    out.to_csv(a.output, index=False)
    print(f"scored {len(out):,} customers -> {a.output}\n{out['risk_tier'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
