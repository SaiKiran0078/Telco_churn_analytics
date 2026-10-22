"""Load the cleaned data (and model scores) into SQLite, run every query in sql/churn_analysis.sql, save CSVs."""
import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from churn.config import CLEAN, TABLES  # noqa: E402


def run(sql_path=ROOT / "sql" / "churn_analysis.sql", verbose=True):
    con = sqlite3.connect(":memory:")
    pd.read_csv(CLEAN).to_sql("customers", con, index=False)
    scores = TABLES / "customer_risk_scores.csv"
    if scores.exists():
        pd.read_csv(scores).to_sql("scores", con, index=False)
    text = Path(sql_path).read_text()
    blocks = re.split(r"^-- name: ", text, flags=re.M)[1:]
    out = {}
    for b in blocks:
        name, _, body = b.partition("\n")
        if "scores" in body and not scores.exists():
            continue
        df = pd.read_sql_query(body, con)
        out[name.strip()] = df
        df.to_csv(TABLES / f"sql_{name.strip()}.csv", index=False)
        if verbose:
            print(f"\n--- {name.strip()} ---\n{df.to_string(index=False)}")
    return out


if __name__ == "__main__":
    run()
