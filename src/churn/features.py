"""Feature engineering and the preprocessing pipeline."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import SERVICE_COLS

NUMERIC = ["tenure", "MonthlyCharges", "TotalCharges", "NumServices", "ChargesPerService", "AvgMonthlySpend", "ChargeVsExpected"]
CATEGORICAL = ["gender", "SeniorCitizen", "Partner", "Dependents", "PhoneService", "MultipleLines", "InternetService",
               "Contract", "PaperlessBilling", "PaymentMethod"] + SERVICE_COLS


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derived columns. All use only information known at scoring time (no leakage from the churn label)."""
    out = df.copy()
    out["NumServices"] = (out[SERVICE_COLS] == "Yes").sum(axis=1) + (out["PhoneService"] == "Yes").astype(int) + (out["InternetService"] != "No").astype(int)
    out["ChargesPerService"] = out["MonthlyCharges"] / out["NumServices"].clip(lower=1)
    out["AvgMonthlySpend"] = np.where(out["tenure"] > 0, out["TotalCharges"] / out["tenure"].clip(lower=1), out["MonthlyCharges"])
    out["ChargeVsExpected"] = out["MonthlyCharges"] - out["AvgMonthlySpend"]  # Positive means current charge is above average spend to date.
    return out


def build_preprocessor(scale: bool = True) -> ColumnTransformer:
    num = Pipeline([("scale", StandardScaler())]) if scale else "passthrough"
    return ColumnTransformer(
        [("num", num, NUMERIC), ("cat", OneHotEncoder(handle_unknown="ignore", drop="if_binary"), CATEGORICAL)],
        verbose_feature_names_out=False,
    )
