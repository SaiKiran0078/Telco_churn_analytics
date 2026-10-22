#!/usr/bin/env python3
"""Point the Power BI project at this repository's data.

Power Query cannot use relative paths, so the report has one Text parameter, RepoRoot,
that must hold the absolute path of this folder. The report reads
    <RepoRoot>\\data\\raw\\Telco-Customer-Churn.csv
    <RepoRoot>\\reports\\tables\\customer_risk_scores.csv, decile_table.csv, permutation_importance.csv
This script checks those files and rewrites the RepoRoot line in expressions.tmdl.

Run it on the machine where Power BI Desktop runs (Windows):
    python scripts/init.py            # set RepoRoot to this clone
    python scripts/init.py --reset    # restore the placeholder before committing
    python scripts/init.py --check    # only validate the data files
    python scripts/init.py --path D:\\work\\telco-churn-analytics   # set an explicit path instead
"""
import argparse, csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TMDL = ROOT / "powerbi" / "Telco Churn Report.SemanticModel" / "definition" / "expressions.tmdl"
PLACEHOLDER = r"C:\telco-churn-analytics"
LINE = re.compile(r'^(expression RepoRoot = ")(.*?)(" meta \[)', re.M)
FILES = {  # file -> (expected rows, expected columns)
    "data/raw/Telco-Customer-Churn.csv": (7043, 21),
    "reports/tables/customer_risk_scores.csv": (7043, 9),
    "reports/tables/decile_table.csv": (10, 7),
    "reports/tables/permutation_importance.csv": (None, 3),
}

def check():
    ok = True
    for rel, (rows, cols) in FILES.items():
        f = ROOT / rel
        if not f.exists():
            print(f"MISSING: {rel}" + ("  (run: python scripts/run_all.py)" if rel.startswith("reports") else "")); ok = False; continue
        with f.open(newline="", encoding="utf-8") as fh:
            data = list(csv.reader(fh))
        n, c = len(data) - 1, len(data[0])
        bad = (rows is not None and n != rows) or c != cols
        print(f"{'WARNING' if bad else 'ok     '} {rel}: {n:,} rows, {c} columns" + (f" (expected {rows} x {cols})" if bad else ""))
        ok &= not bad
    return ok

def set_path(value):
    text = TMDL.read_bytes().decode("utf-8")
    if not LINE.search(text):
        sys.exit("ERROR: RepoRoot line not found in expressions.tmdl")
    TMDL.write_bytes(LINE.sub(lambda m: m.group(1) + value + m.group(3), text, count=1).encode("utf-8"))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--reset", action="store_true"); g.add_argument("--check", action="store_true")
    ap.add_argument("--path", help="explicit absolute path to use for RepoRoot")
    a = ap.parse_args()
    if a.reset:
        set_path(PLACEHOLDER); print("RepoRoot reset to", PLACEHOLDER); return
    ok = check()
    if a.check: sys.exit(0 if ok else 1)
    value = a.path or str(ROOT)
    if re.match(r"^[A-Za-z]:", value) or sys.platform == "win32":
        value = value.replace("/", "\\")
    elif not a.path:
        print("NOTE: this is not Windows. Power BI Desktop reads the path on the machine where it runs;"
              " use --path with the Windows path if you work in WSL or a VM.")
    set_path(value.rstrip("\\/"))
    print("RepoRoot set to", value)
    print('Next: open "powerbi/Telco Churn Report.pbip" in Power BI Desktop and click Refresh.')
    print("Before committing run:  python scripts/init.py --reset")

if __name__ == "__main__":
    main()
