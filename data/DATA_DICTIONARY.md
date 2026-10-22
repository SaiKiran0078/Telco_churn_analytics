# Data dictionary

**Source.** `data/raw/Telco-Customer-Churn.csv` is the public sample dataset distributed in IBM's repository [IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d) (Apache-2.0 licence). It describes customers of a fictional telecom company. It is **sample data**: the project demonstrates a method, and the results are not benchmarks for any real operator. The file is included unchanged.

**Grain.** One row per customer, 7,043 rows, one snapshot in time (no dates).

| Column | Type | Meaning |
|---|---|---|
| customerID | text | Unique customer key |
| gender | Female / Male | |
| SeniorCitizen | 0/1 raw, Yes/No cleaned | Customer is a senior citizen |
| Partner, Dependents | Yes / No | Lives with a partner / has dependents |
| tenure | integer, months (0-72) | Months as a customer |
| PhoneService | Yes / No | |
| MultipleLines | Yes / No | More than one phone line (cleaned: "No phone service" -> No) |
| InternetService | DSL / Fiber optic / No | |
| OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies | Yes / No | Add-on service (cleaned: "No internet service" -> No) |
| Contract | Month-to-month / One year / Two year | |
| PaperlessBilling | Yes / No | |
| PaymentMethod | Electronic check / Mailed check / Bank transfer / Credit card | "(automatic)" suffix removed in cleaning |
| MonthlyCharges | $ | Current monthly bill |
| TotalCharges | $ | Total billed to date (11 blanks in raw data fixed to 0, see below) |
| Churn | Yes / No | **Target.** Customer left in the last month |

## Added during cleaning and feature engineering
| Column | Meaning |
|---|---|
| ChurnFlag | Churn as 0/1 |
| NumServices | Count of products held (phone, internet, and each add-on) |
| ChargesPerService | MonthlyCharges / NumServices |
| AvgMonthlySpend | TotalCharges / tenure (MonthlyCharges when tenure is 0) |
| ChargeVsExpected | MonthlyCharges minus AvgMonthlySpend; positive means the current monthly charge is above average monthly spend to date, which does not by itself prove a price increase |

## Data quality facts (details in `notebooks/01_data_cleaning_and_quality.ipynb`)
- No duplicate rows or customer IDs. No missing values as read.
- `TotalCharges` is text because **11 values are blank**. All 11 are customers with tenure 0 (not yet billed), so they are set to 0.
- TotalCharges ~ tenure x MonthlyCharges for 99.6% of customers (within 25%), so the billing columns are internally consistent.
- Churn rate: 26.5% (1,869 of 7,043).

## Generated files
`data/processed/telco_clean.csv` (cleaned table), `reports/tables/*.csv` (all result tables), `reports/tables/customer_risk_scores.csv` (a score, risk tier, segment and recommended action for every customer).
