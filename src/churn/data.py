"""Load and clean the raw Telco churn file. Every cleaning decision is logged so it can be reported."""
import pandas as pd

from .config import RAW, SERVICE_COLS

BINARY_NO_SERVICE = SERVICE_COLS + ["MultipleLines"]


def load_raw(path=RAW) -> pd.DataFrame:
    return pd.read_csv(path)


def quality_report(df: pd.DataFrame) -> dict:
    """Facts about the raw file, before any cleaning."""
    tc = pd.to_numeric(df["TotalCharges"], errors="coerce")
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_customer_ids": int(df["customerID"].duplicated().sum()),
        "missing_cells_as_read": int(df.isna().sum().sum()),
        "total_charges_not_numeric": int(tc.isna().sum()),
        "total_charges_blank_with_tenure_zero": int(((df["TotalCharges"].str.strip() == "") & (df["tenure"] == 0)).sum()),
        "churn_rate_pct": round(float((df["Churn"] == "Yes").mean() * 100), 2),
    }


def clean(df: pd.DataFrame):
    """Return (clean_df, log). The log lists each fix with the number of rows it touched."""
    df = df.copy()
    log = []

    df.columns = [c.strip() for c in df.columns]
    df["customerID"] = df["customerID"].str.strip()

    # 1. TotalCharges arrives as text because 11 rows are blank. Those are brand-new customers (tenure = 0)
    #    who have not been billed yet, so the right value is 0, not a guess.
    blank = df["TotalCharges"].str.strip().eq("")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].str.strip().replace("", pd.NA), errors="coerce")
    new_customers = blank & df["tenure"].eq(0)
    df.loc[new_customers, "TotalCharges"] = 0.0
    log.append(("TotalCharges: blank text -> 0.0 (customers with tenure 0, not billed yet)", int(new_customers.sum())))
    assert df["TotalCharges"].notna().all(), "unexpected unresolved TotalCharges"

    # 2. 'No internet service' / 'No phone service' are the same fact as 'No' for the add-on question.
    for col in BINARY_NO_SERVICE:
        n = int(df[col].isin(["No internet service", "No phone service"]).sum())
        df[col] = df[col].replace({"No internet service": "No", "No phone service": "No"})
        log.append((f"{col}: 'No internet/phone service' -> 'No'", n))

    # 3. SeniorCitizen is 0/1 while every other flag is Yes/No: make them consistent.
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    log.append(("SeniorCitizen: 0/1 -> No/Yes", int(len(df))))

    # 4. Target as 0/1 for modelling; keep the readable label too.
    df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)

    # 5. Strip the '(automatic)' wording so payment-method labels are short in charts.
    df["PaymentMethod"] = df["PaymentMethod"].str.replace(" (automatic)", "", regex=False)
    log.append(("PaymentMethod: removed ' (automatic)' suffix", int(df["PaymentMethod"].isin(["Bank transfer", "Credit card"]).sum())))

    # 6. Sanity checks that would fail loudly if the source changed.
    assert df["customerID"].is_unique
    assert df["tenure"].between(0, 100).all()
    assert (df["MonthlyCharges"] > 0).all()
    assert set(df["Churn"].unique()) <= {"Yes", "No"}
    return df, log


def tenure_bucket(t: pd.Series) -> pd.Series:
    return pd.cut(t, [-1, 6, 12, 24, 48, 72], labels=["0-6 m", "7-12 m", "13-24 m", "25-48 m", "49-72 m"])
