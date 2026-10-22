"""Rebuild the whole project from the raw CSV: clean -> EDA -> model -> segments -> SQL. Run: python scripts/run_all.py"""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent
for s in ["build_01_02.py", "build_03.py", "build_04.py", "run_sql.py"]:
    print(f"\n=== {s} ===", flush=True)
    subprocess.run([sys.executable, str(here / s)], check=True, cwd=here)
