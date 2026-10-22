<div align="center">
  <img src="docs/images/project-banner.png" alt="Telco Customer Churn Analytics project banner" width="100%" />

  # Telco Customer Churn Analytics

  **From customer churn analysis to risk-based retention decisions**

  <p>
    <a href="https://github.com/SaiKiran0078/Telco_churn_analytics/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/SaiKiran0078/Telco_churn_analytics/ci.yml?branch=main&label=CI" alt="Continuous integration status" /></a>
    <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB?logo=python&logoColor=white" alt="Python 3.11 and 3.13" />
    <img src="https://img.shields.io/badge/SQL-SQLite%20%7C%20SQL%20Server-4479A1?logo=databricks&logoColor=white" alt="SQLite and SQL Server" />
    <img src="https://img.shields.io/badge/Power%20BI-PBIP-F2C811?logo=powerbi&logoColor=222222" alt="Power BI project" />
    <img src="https://img.shields.io/badge/scikit--learn-Churn%20Model-F7931E?logo=scikitlearn&logoColor=white" alt="scikit-learn model" />
  </p>

  *An end-to-end analytics case study combining data quality, exploratory analysis, SQL, predictive modelling, customer risk prioritization, and an interactive five-page Power BI report.*
</div>

---

## Contents

- [Project overview](#project-overview)
- [Business snapshot](#business-snapshot)
- [Power BI report preview](#power-bi-report-preview)
- [Key findings](#key-findings-and-business-implications)
- [Project deliverables](#project-deliverables)
- [Technology and skills](#technology-and-skills-demonstrated)
- [Quick start](#quick-start)
- [Run the SQL analyses](#run-the-sql-analyses)
- [Open the Power BI report](#open-the-power-bi-report)
- [Repository structure](#repository-structure)
- [Reproducibility and tests](#reproducibility-and-tests)
- [Documentation](#documentation)
- [Limitations and responsible use](#limitations-and-responsible-use)
- [Data source and license](#data-source-and-license)

## Project overview

Customer churn can reduce recurring revenue and increase the effort required to replace customers. This project uses the **IBM public Telco Customer Churn sample dataset** to explore churn patterns, identify customer groups associated with higher churn, quantify monthly charges associated with customers already labelled as churned, rank customer records by modelled churn risk, and explore retention-campaign scenarios.

The repository is built as a **reproducible data analyst / analytics engineering portfolio project**. It combines data cleaning, exploratory and statistical analysis, SQL, Python machine learning, customer segmentation, automated checks, and Power BI storytelling. The project is a case study—not a production churn service—and its snapshot-based scores are not validated forecasts of future behaviour.

**Recommended starting points:**

- Read the [project report](PROJECT_REPORT.md) for the business questions, methodology, results, and recommendations.
- Open the Power BI `.pbip` project using the [Power BI setup guide](docs/POWERBI_GUIDE.md).
- Review the [model card](docs/MODEL_CARD.md) for evaluation, appropriate use, and limitations.
- See the [data dictionary](data/DATA_DICTIONARY.md) for source fields and data-quality notes.

## Business snapshot

| Measure | Result |
|---|---:|
| Customers in the sample | 7,043 |
| Customers labelled as churned | 1,869 |
| Overall churn rate | 26.5% |
| Total current monthly charges in the snapshot | About $456,117 |
| Monthly charges associated with customers labelled as churned | About $139,131 |
| Share of current monthly charges associated with churned customers | 30.5% |
| Held-out test ROC-AUC | 0.842 |
| Held-out test PR-AUC | 0.636 |
| Churners captured in the top-scored 20% of the held-out test population | 50.5% |

**Metric interpretation:** the $139,131 value is the sum of current monthly charges for records whose churn label is `Yes`. The data is a single snapshot, so this value is not a measured future loss or a guarantee of revenue a retention campaign could recover. Model metrics describe the evaluation split used in this project and may not generalize to a new population or time period.

## Power BI report preview

The Power BI report is organized into five stakeholder-focused pages: executive overview, churn drivers, revenue at risk, churn risk prioritization, and a retention ROI simulator. The images below are static previews. Open the `.pbip` file in Power BI Desktop to interact with the report, slicers, cross-filtering, and scenario controls.

<details open>
  <summary><strong>1 · Executive overview</strong></summary>
  <img src="docs/images/powerbi-page1-executive-overview.png" alt="Executive overview with churn KPIs and customer breakdowns" width="100%" />
</details>

<details>
  <summary><strong>2 · Churn drivers</strong></summary>
  <img src="docs/images/powerbi-page2-churn-drivers.png" alt="Churn drivers across tenure, contract, services, and billing attributes" width="100%" />
</details>

<details>
  <summary><strong>3 · Revenue at risk</strong></summary>
  <img src="docs/images/powerbi-page3-revenue-at-risk.png" alt="Monthly charges associated with churn and customer segment breakdowns" width="100%" />
</details>

<details>
  <summary><strong>4 · Churn risk and retention priorities</strong></summary>
  <img src="docs/images/powerbi-page4-churn-risk.png" alt="Model performance, risk tiers, feature importance, and customer call list" width="100%" />
</details>

<details>
  <summary><strong>5 · Retention campaign ROI simulator</strong></summary>
  <img src="docs/images/powerbi-page5-retention-roi.png" alt="Retention campaign scenario controls, costs, and estimated net value" width="100%" />
</details>

## Key findings and business implications

- **Contract type is strongly associated with churn.** Month-to-month customers account for about 55% of the customer base and 88.6% of churned records; 42.7% of customers in that contract group are labelled as churned. The two-year contract group has a 2.8% churn rate in this sample.
- **Early tenure is a risk period.** The 0–6 month tenure cohort has a 52.9% churn rate, compared with 9.5% for the 49–72 month cohort.
- **Risk and charges are concentrated in identifiable groups.** The month-to-month + fiber optic + electronic-check group contains 1,307 records, has a 60.4% churn rate, and has about $68.3K in monthly charges associated with churn. This is a different group definition from the rule-based month-to-month fiber group without online security or tech support.
- **Protective services are associated with lower churn.** Among customers with internet service, churn is 56.7% for customers with none of four protection/support services and 5.3% for customers with all four. This is an observed association, not proof that adding a service causes churn to fall.
- **Risk ranking may help prioritize outreach.** The top-scored 20% of the held-out test population contains 50.5% of its churned customers. These retrospective scores should not be treated as validated prospective predictions.
- **Retention economics are assumption-dependent.** Offer cost, expected save rate, and the revenue-retention horizon are scenario inputs. Validate the effect through a controlled experiment before scaling a campaign.

See [PROJECT_REPORT.md](PROJECT_REPORT.md) for full methodology, more findings, and recommendations.

## Project deliverables

| Deliverable | Files and folders | What it demonstrates |
|---|---|---|
| Data cleaning and quality checks | `notebooks/01_data_cleaning_and_quality.ipynb`, `src/churn/data.py`, `data/processed/` | Missing-value handling, type conversion, quality checks, and a cleaned analysis table |
| Exploratory and statistical analysis | `notebooks/02_eda_business_analysis.ipynb`, `reports/figures/`, `reports/tables/` | Churn breakdowns, tenure cohorts, associations, and revenue-at-risk summaries |
| Predictive modelling | `notebooks/03_modeling.ipynb`, `src/churn/modeling.py`, `models/churn_model.joblib` | Preprocessing/model pipeline, model comparison, held-out evaluation, and risk scoring |
| Segmentation and retention strategy | `notebooks/04_segments_risk_and_strategy.ipynb`, `src/churn/`, `reports/tables/` | Customer profiles, risk tiers, campaign strategies, and ROI sensitivity analysis |
| SQLite SQL analysis | `sql/churn_analysis.sql`, `scripts/run_sql.py` | Named SQL queries run automatically as part of the reproducible pipeline |
| SQL Server analysis | `sql/churn_analysis_sql_server.sql` | Separate Microsoft SQL Server / T-SQL version for use in SQL Server tools |
| Interactive BI report | `powerbi/Telco Churn Report.pbip`, `powerbi/Telco Churn Report.Report/`, `powerbi/Telco Churn Report.SemanticModel/` | Five-page report, semantic model, DAX measures, slicers, cross-filtering, and scenario controls |
| Tests and automation | `tests/`, `scripts/validate_pbip.py`, `.github/workflows/ci.yml` | Unit tests, pipeline smoke checks, Power BI structure/reference checks, and GitHub Actions CI |

## Technology and skills demonstrated

| Area | Technologies and methods |
|---|---|
| Data analysis | Python, pandas, NumPy, data cleaning, validation, missing-value handling, exploratory analysis |
| Statistics | Cohort comparisons, chi-square tests, Mann–Whitney tests, effect sizes, association analysis |
| SQL | CTEs, joins, conditional aggregation, window functions, grouping, churn KPIs, Pareto/cumulative summaries; SQLite and SQL Server T-SQL dialects |
| Machine learning | scikit-learn pipelines, feature engineering, stratified train/test split, cross-validation, model comparison, ROC-AUC, PR-AUC, Brier score, threshold selection |
| Business intelligence | Power BI Project (`.pbip`), semantic model, DAX, slicers, cross-filtering, KPIs, risk tiers, ROI scenario modelling |
| Engineering and reproducibility | Python package structure, command-line entry point, automated tests, Git, Power BI reference validation, GitHub Actions |
| Business communication | Executive reporting, segment interpretation, revenue-at-risk framing, prioritization, limitations, experiment recommendations |

## Quick start

### Requirements

- Python **3.13 recommended**. The package requires Python 3.11 or later, and CI is configured for Python 3.11 and 3.13.
- Power BI Desktop on Windows if you want to open and refresh the interactive report.
- Git if cloning the repository; otherwise, download and extract the project ZIP.

### 1. Clone the repository

```powershell
git clone https://github.com/SaiKiran0078/Telco_churn_analytics.git
cd Telco_churn_analytics
```

Alternatively, download the ZIP from GitHub and open PowerShell in the extracted project folder.

### 2. Create a virtual environment and install dependencies

In Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

If Python 3.13 is not installed, use another Python version supported by the project (3.11 or later), for example `py -3.11 -m venv .venv`. If PowerShell blocks environment activation, you can invoke the environment's Python directly as `.\.venv\Scripts\python.exe` or use an approved activation-policy setting for your machine.

The dependencies in `requirements.txt` include a pinned scikit-learn version to match the included serialized model. Keep that version aligned when loading `models/churn_model.joblib`; loading a model saved with a different scikit-learn version may be unreliable.

### 3. Verify the inputs and run the tests

```powershell
python scripts/init.py --check
python -m unittest discover -s tests -v
```

The optional Power BI JSON-schema test uses Microsoft's schema repository and is skipped when `MS_SCHEMAS` is not configured. The remaining tests do not require Power BI Desktop.

### 4. Rebuild the project outputs

```powershell
python scripts/run_all.py
```

The end-to-end script runs the build steps for data cleaning and EDA, modelling, segments/risk analysis, and SQL. It regenerates the cleaned dataset, figures, tables, metrics, saved model, and SQL result CSVs. Check the resulting file changes before committing regenerated artefacts.

To run only the SQL analysis **after the cleaned dataset has been generated**, use:

```powershell
python scripts/run_sql.py
```

### 5. Score a customer CSV (optional)

```powershell
python -m churn.predict --input path\to\new_customers.csv --output scored.csv
```

The input should contain the raw dataset's customer feature columns; `Churn` can be absent when scoring new records. The output includes the customer key, selected customer attributes, churn probability, and risk tier. Review `.gitignore` before adding any one-off exports or customer-level data to version control. This command does not make the model a validated production predictor.

## Run the SQL analyses

The repository deliberately keeps **two SQL dialects**. They serve different purposes and should not be swapped or renamed into one file.

### SQLite version — used by the Python pipeline

File: [`sql/churn_analysis.sql`](sql/churn_analysis.sql)

This file contains named query blocks that `scripts/run_sql.py` reads and executes against an in-memory SQLite database. The runner loads the cleaned `customers` table from `data/processed/telco_clean.csv` and loads the `scores` table if `reports/tables/customer_risk_scores.csv` exists. Run `python scripts/run_all.py` first so the expected analysis data and model scores are available.

The queries cover:

| Query name | Business question / purpose |
|---|---|
| `00_source_table_check` | Confirm the input table was loaded |
| `00_row_count` | Count the records available to the SQL analyses |
| `00_preview_top_10` | Preview sample rows and check the imported columns |
| `01_headline_kpis` | Summarize customers, churners, churn rate, and monthly charges |
| `02_churn_by_contract` | Compare churn by contract type, including customer/churn shares |
| `03_tenure_cohorts` | Compare churn across tenure groups |
| `04_pareto_of_revenue_lost` | Rank contract/service/payment combinations and summarize concentration |
| `05_services_and_churn` | Compare churn across protection and support services |
| `06_highest_risk_group` | Profile a rule-based high-risk customer group |
| `07_payment_by_contract` | Examine payment-method patterns within contract type |
| `08_call_list_top_revenue_at_risk` | Rank high-risk active customers by monthly charges when model scores exist |
| `09_churn_by_internet_service` | Compare churn for fiber, DSL, and customers without internet service |
| `10_monthly_charges_from_churned_by_contract` | Summarize current monthly charges associated with churned records by contract |
| `11_churn_by_payment_method` | Compare churn across payment methods |

Each executed query writes a CSV to `reports/tables/sql_<query_name>.csv`. The pipeline output tables are intended for review and comparison with the Python analysis. Query `08_call_list_top_revenue_at_risk` is skipped if model score output is not present.

### SQL Server version — for SQL Server tools

File: [`sql/churn_analysis_sql_server.sql`](sql/churn_analysis_sql_server.sql)

This is the standalone Microsoft SQL Server / T-SQL script for manual practice or analysis in SQL Server Management Studio (SSMS) or another compatible SQL Server client. It expects a database named `TelcoChurn` and an imported source table named `dbo.TelcoChurn` with the expected columns. Import the source CSV and confirm the table/column names before executing the script. It uses SQL Server-specific constructs such as `USE`, `GO`, `OBJECT_ID`, and `TOP` and is **not** the script used by `scripts/run_sql.py`.

Both files are read-only analysis scripts; review the SQL and validate the source schema before running against any non-sample database.

## Open the Power BI report

1. From the repository root, run `python scripts/init.py`. This sets the report's `RepoRoot` parameter to the current local path.
2. Open `powerbi/Telco Churn Report.pbip` in Power BI Desktop.
3. Refresh the report and resolve any Power BI Desktop prompts for local data access.
4. Before committing, run `python scripts/init.py --reset` to restore the generic placeholder path instead of committing a machine-specific path.

Power Query requires an absolute local path, so initialize the project after moving or extracting it to a new folder. See the [Power BI setup guide](docs/POWERBI_GUIDE.md) and [DAX measure reference](docs/POWERBI_MEASURES.md). Static page previews are included in `docs/images/`.

## Repository structure

```text
Telco_churn_analytics/
├── .github/
│   └── workflows/
│       └── ci.yml                   # Python test matrix and Power BI validation
├── data/
│   ├── raw/
│   │   └── Telco-Customer-Churn.csv  # Public source sample
│   ├── processed/
│   │   └── telco_clean.csv           # Generated cleaned dataset
│   └── DATA_DICTIONARY.md             # Source, field definitions, quality notes
├── docs/
│   ├── images/                       # Banner, report previews, layout references
│   ├── MODEL_CARD.md                 # Model evaluation, purpose, limitations
│   ├── POWERBI_GUIDE.md              # Report setup and troubleshooting
│   └── POWERBI_MEASURES.md           # DAX measure reference
├── models/
│   └── churn_model.joblib            # Generated scikit-learn pipeline
├── notebooks/
│   ├── 01_data_cleaning_and_quality.ipynb
│   ├── 02_eda_business_analysis.ipynb
│   ├── 03_modeling.ipynb
│   └── 04_segments_risk_and_strategy.ipynb
├── powerbi/
│   ├── Telco Churn Report.pbip       # Power BI Project entry point
│   ├── Telco Churn Report.Report/    # Report definition
│   └── Telco Churn Report.SemanticModel/ # Semantic model definition
├── reports/
│   ├── figures/                      # Analysis, model, and strategy charts
│   ├── tables/                       # KPI, model, segment, risk, and SQL CSVs
│   └── metrics.json                  # Evaluation metrics and configuration details
├── scripts/
│   ├── build_01_02.py                # Cleaning and EDA outputs
│   ├── build_03.py                   # Modelling and evaluation outputs
│   ├── build_04.py                   # Segments, risk, strategy and ROI outputs
│   ├── init.py                       # Initialize or reset local Power BI path
│   ├── run_all.py                    # Run the full pipeline
│   ├── run_sql.py                    # Execute named SQLite queries and export CSVs
│   └── validate_pbip.py              # Power BI project validation helper
├── sql/
│   ├── churn_analysis.sql            # Named SQLite query blocks used by pipeline
│   └── churn_analysis_sql_server.sql # Standalone Microsoft SQL Server T-SQL script
├── src/churn/                        # Reusable data, feature, model, and scoring code
├── tests/                            # Cleaning, scoring, SQL parity, Power BI checks
├── CHANGELOG.md
├── LICENSE
├── Makefile
├── PROJECT_REPORT.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

Generated files such as figures, tables, the cleaned dataset, and the saved model are stored in the repository so readers can inspect example outputs without running the entire pipeline first. Rebuilding the pipeline may update them.

## Reproducibility and tests

Run from the repository root after dependency installation:

| Check | Command | Purpose |
|---|---|---|
| Validate expected input/output files | `python scripts/init.py --check` | Check the local project inputs and expected artefacts |
| Rebuild the end-to-end analysis | `python scripts/run_all.py` | Recreate data, analysis, model, and SQL outputs |
| Run the unit test suite | `python -m unittest discover -s tests -v` | Validate data cleaning, prediction, SQL parity, and related behaviour |
| Run SQL analyses only | `python scripts/run_sql.py` | Execute the SQLite named queries and save CSV outputs |
| Check Power BI references | `python scripts/check_refs.py powerbi` | Check Power BI field references |
| Validate Power BI files | `python scripts/validate_pbip.py` | Run structural validation helper |
| Show scoring command options | `python -m churn.predict --help` | Smoke-test the installed package entry point |

The GitHub Actions workflow in `.github/workflows/ci.yml` runs the build pipeline, prediction entry-point smoke test, and unit tests on Python 3.11 and 3.13. A separate job installs the optional development dependencies, retrieves Microsoft's Power BI JSON schemas, and runs the Power BI validation tests. Schema checks provide useful automated validation but cannot guarantee that every visual will render identically across Power BI Desktop versions.

## Documentation

- [Project report — methodology, findings, recommendations](PROJECT_REPORT.md)
- [Data dictionary — source and field definitions](data/DATA_DICTIONARY.md)
- [Model card — evaluation, intended use, limitations](docs/MODEL_CARD.md)
- [Power BI setup guide](docs/POWERBI_GUIDE.md)
- [Power BI DAX measure reference](docs/POWERBI_MEASURES.md)
- [Changelog](CHANGELOG.md)
- [MIT License](LICENSE)

## Limitations and responsible use

- The dataset is a public sample for a fictional telecom provider. It is not a real telecom operator's current customer base and should not be used as an industry benchmark.
- The data contains a single snapshot without customer event dates. The model does not predict when an individual will leave and has not been validated as a forward-looking production model.
- Observed relationships do not establish causation. A protective service or a retention offer is not guaranteed to reduce churn.
- Model performance, calibration, and risk rankings can change across populations and time periods. Validate on appropriate time-based data before operational use.
- ROI outputs depend on assumptions about offer cost, save rate, and how long retained revenue is counted. Validate with a controlled test before scaling.
- Use risk scores to support human-reviewed outreach, not to deny service, make automatic pricing decisions, or unfairly limit customer options.
- Treat customer-level exports as sensitive. Do not commit real customer information, credentials, machine-specific paths, or private data to a public repository.

## Data source and license

The dataset is the IBM Telco Customer Churn public sample. More information and field definitions are documented in the [data dictionary](data/DATA_DICTIONARY.md). Project code is distributed under the [MIT License](LICENSE).
