"""Project-wide paths and business assumptions (change them here, results update everywhere)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
CLEAN = ROOT / "data" / "processed" / "telco_clean.csv"
FIG = ROOT / "reports" / "figures"
TABLES = ROOT / "reports" / "tables"
MODELS = ROOT / "models"
RANDOM_STATE = 42

# Business assumptions for the retention-campaign simulation (illustrative; documented in PROJECT_REPORT.md).
ASSUMPTIONS = {
    "offer_cost": 50.0,            # cost of one retention offer, in dollars
    "offer_success_rate": 0.30,    # share of would-be churners a retention offer keeps
    "horizon_months": 12,          # value of a retained customer = monthly charge x this many months
}

SERVICE_COLS = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
