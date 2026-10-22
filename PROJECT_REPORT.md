# Project report: reducing customer churn at a telecom company

*A data analyst + data scientist case study: from raw file to a prioritised retention plan.*

## 1. Executive summary
In this sample, **26.5% of customers have a churn label**. Their monthly charges sum to about **$139k**, or 30.5% of the $456k total monthly charges in the snapshot. I cleaned the data, identified patterns associated with churn, built a model to rank risk, and evaluated a costed retention scenario.

**What I found**
- **Contract type is the biggest lever.** Month-to-month customers are 55% of the base but **88.6% of all churners** (42.7% churn). Two-year customers churn at 2.8%.
- **Early tenure is a key risk period.** Customers in the 0–6 month tenure cohort have a 52.9% churn rate; the rate falls to 9.5% for the 49–72 month cohort.
- **The largest revenue-loss combination is concentrated.** The 1,307 customers on month-to-month fiber plans paying by electronic check have a **60.4% churn rate** and about **$68.3k in monthly charges associated with churn**, approximately **49.1% of total MRR associated with churn**. Separately, the SQL rule-based group of month-to-month fiber customers without online security or tech support contains 1,524 customers (21.6% of the base), churns at 60.7%, and accounts for 49.5% of all churners.
- **Protection services work like a seatbelt.** Among internet customers, churn falls from **56.7% with no protective service to 5.3% with all four** (security, backup, device protection, tech support).
- **A model can rank customers well:** ROC-AUC **0.84** on unseen customers. The 20% highest-risk customers contain **half of all churners**.
- **The business case is robust.** A model-targeted campaign is worth about **$36.9k per 1,000 customers**, versus $32.1k for contacting every month-to-month customer and $19.5k for contacting everyone. It breaks even if just **10%** of at-risk customers are retained (assumed: 30%).

**Recommendation.** Run a targeted retention programme on the High-risk tier (22% of customers, 66% churn), led by (1) a bill credit for switching to auto-pay plus a 12-month contract for electronic-check fiber customers and (2) bundled security / tech-support offers at sign-up. Measure the true success rate with an A/B test before scaling.

## 2. The business problem
Retention is cheaper than acquisition, but a retention team can only call so many customers. They need to know **who is leaving, why, how much it costs, and whom to call first**.

| Stakeholder question | Where answered |
|---|---|
| How bad is churn, in customers and in money? | Notebook 02 §1, SQL 01 |
| Which customers churn and why? | Notebook 02 §2-6, SQL 02-07 |
| Can we predict it? Who should be called first? | Notebook 03, `customer_risk_scores.csv` |
| What kinds of customers do we have and what should we do for each? | Notebook 04 §1, playbook below |
| Is a campaign worth the money? | Notebook 03 §7, Notebook 04 §3 |

## 3. Data
7,043 customers, 21 columns, one snapshot (IBM public sample dataset; see `data/DATA_DICTIONARY.md`). It is sample data for a fictional company, so the **method** is the deliverable and numbers should not be read as industry benchmarks.

## 4. What I did

### 4.1 Data cleaning and quality (Notebook 01, `src/churn/data.py`)
| Problem found | Fix | Why |
|---|---|---|
| `TotalCharges` read as text: 11 blank values | Set to 0 | All 11 are customers with tenure 0 who haven't been billed yet. Dropping them would remove 11 active customers; a median fill would invent revenue. |
| "No internet service" / "No phone service" in 7 columns (up to 1,526 rows each) | Recoded to "No" | Same fact as "No" for the add-on question; avoids redundant categories. |
| `SeniorCitizen` coded 0/1, all other flags Yes/No | Recoded | Consistency. |
| Long labels such as "Bank transfer (automatic)" | Shortened | Readable charts. |
| Duplicates, impossible values, billing consistency | Checked, none found | TotalCharges within 25% of tenure x monthly charge for 99.6% of customers. |

Every fix is logged (`reports/tables/cleaning_log.csv`) and enforced by unit tests that fail if the source changes.

### 4.2 Exploratory and business analysis (Notebook 02, SQL)
- KPIs and revenue at risk, churn by every key attribute, tenure cohorts, contract x tenure heatmap.
- **Statistics, not just charts:** chi-square tests with Cramér's V effect sizes for categories, Mann-Whitney tests with rank-biserial effect sizes for numbers. Contract (V = 0.41), internet service (0.32) and payment method (0.30) are the strongest; **gender and phone service are not significant** (p > 0.3).
- **Eight SQL queries** (CTEs, window functions, Pareto with cumulative share, joins to model scores). A unit test checks the SQL answers equal the pandas answers.
- Finding worth noting: the electronic-check effect **survives controlling for contract**: among month-to-month customers, electronic-check payers churn at 53.7% vs 31.6-34.1% for other methods.

### 4.3 Predictive modelling (Notebook 03, `src/churn`)
- **Features:** four engineered (number of services, charge per service, average spend to date, and the difference between current monthly charge and average spend to date), none directly using the churn label.
- **Honest validation:** stratified 80/20 split, 5-fold CV on training data only, test set used once. Selection rule fixed in advance.
- **Models compared:** baseline, logistic regression, random forest, gradient boosting; two tuned with randomised search. All real models score within 0.002 ROC-AUC (0.843-0.845): the signal is largely additive, so I chose the **simpler, explainable logistic regression**.
- **Results (test):** ROC-AUC 0.842 (95% CI 0.819-0.864), PR-AUC 0.636 vs 0.265 base rate, Brier 0.138, well calibrated.
- **Drivers:** tenure dominates (shuffling it costs 0.17 AUC, three times anything else), then internet service and contract. Odds ratios: fiber optic 2.4x, month-to-month 2.0x; each extra standard deviation of tenure (about 25 months) cuts the odds of churn by about 71%.
- **From probability to decision:** the contact threshold (0.27) maximises net campaign value, chosen on out-of-fold *training* predictions so the test result is untouched.
- **Fairness check:** no gender gap. Seniors are flagged more (68% vs 36%), matching their real churn (44% vs 23%), but are ranked less accurately (AUC 0.79 vs 0.84), so actions for them are supportive and human-reviewed.

### 4.4 Segmentation, scoring and strategy (Notebook 04)
Five customer segments from K-means (k = 5 chosen for interpretability; silhouette scores were flat from k = 3 to 6, which I say openly). The churn label is not used to form segments, so differences in churn are a real finding.

| Segment | Customers | Churn | Monthly revenue lost | Recommended action |
|---|---|---|---|---|
| E-check fiber, month-to-month | 1,535 | 47.6% | $57.3k (41%) | Bill credit for switching to auto-pay + 12-month contract |
| Senior fiber, month-to-month | 944 | 48.4% | $37.1k (27%) | Proactive call, senior support, 12-month price lock |
| Mid-tenure month-to-month | 1,501 | 29.9% | $31.0k (22%) | Contract-upgrade offer bundled with security / tech support |
| Loyal multi-service | 1,537 | 7.8% | $11.4k (8%) | Protect: loyalty perks, no discounts needed |
| Phone-only budget | 1,526 | 7.4% | $2.3k (2%) | Low priority |

Every customer also has a cross-validated risk score and tier (`reports/tables/customer_risk_scores.csv`). Each row is held out from its fold-specific model fit, but hyperparameters were selected on the training split; treat these as retrospective portfolio-ranking scores, not prospective production probabilities. The **High tier is 22% of customers, churns at 66% and holds 55% of all churners**; the Low tier (59% of customers) churns at 9%.

### 4.5 Business impact (assumptions stated, then stress-tested)
Assumptions (editable in `src/churn/config.py`): $50 per offer, 30% of would-be churners retained, a saved customer is worth 12 months of their monthly charge.

| Strategy (test set, per 1,000 customers) | Net value |
|---|---|
| Do nothing | $0 |
| Contact everyone | $19.5k |
| Contact all month-to-month customers | $32.1k |
| **Model-targeted (threshold 0.27)** | **$36.9k** (contacts 41% of customers and reaches 78% of churners) |

If the assumptions hold, scaling to this 7,043-customer base is worth roughly **$260k net over 12 months** (a projection, not a measurement). The sensitivity table (`reports/tables/roi_sensitivity.csv`) shows the campaign is profitable unless offers are expensive *and* rarely work; break-even success rate at $50 per offer is **10.4%**.

**Honest reading:** the model beats the simple "call all month-to-month customers" rule by about $4.8k per 1,000 customers (+15%). That is a real but modest gain, so the simple rule is a strong fallback; the model's added value is ordering the calls within groups so the best-value calls come first.

## 5. What this solves
| Before | After |
|---|---|
| "Churn is 26%" with no explanation | Concentration pinpointed: contract, early tenure, fiber + e-check, no protection services |
| Retention calls to everyone or at random | Ranked, tiered list of every customer with a recommended action |
| No idea if a campaign pays | Costed, stress-tested business case with a break-even point |
| Risk of a black-box model | Explainable model, calibration, fairness checks, model card |

## 6. Limitations and next steps
- **One snapshot, no dates.** No time-based validation, survival analysis or churn timing. With dated data I would build a hazard model and monitor drift.
- **Correlation, not causation.** Whether a bill credit or a bundled add-on *causes* retention needs an A/B test; success rate and offer cost are assumptions.
- **Sample data from a fictional company.** Re-validate on real data.
- **Next steps:** A/B test the two top offers; add cost-to-serve and lifetime value; deploy scoring as a monthly batch (`python -m churn.predict`) with monitoring; consider uplift modelling to target customers who are *persuadable*, not just at risk.

## 7. Skills demonstrated
Data cleaning and validation; SQL (CTEs, windows, joins); statistical testing with effect sizes; feature engineering without leakage; model comparison, tuning, calibration and bootstrap intervals; threshold selection from business costs; segmentation; fairness review; model documentation; automated tests and CI; clear business communication.

## 8. Reproduce
From the repository root, install the package and its pinned dependencies with `python -m pip install -e .`, then run `python scripts/run_all.py` to rebuild the notebooks, figures, tables and model from the raw CSV. Run `python -m unittest discover -s tests -v` to run the test suite; the optional Power BI schema test is skipped unless `MS_SCHEMAS` points to a local clone of Microsoft's JSON schemas. The editable install also makes the `python -m churn.predict` scoring command available; see the README for an example.
