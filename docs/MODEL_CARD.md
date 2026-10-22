# Model card: customer churn classifier

**Purpose.** Demonstrate how customer features can be used to rank churn risk in a retrospective portfolio analysis. The sample is a single snapshot and does not document a future prediction horizon, so these scores are not validated forecasts of which customers will leave next. The model supports human review; it must not be used to deny service or change prices automatically.

**Model.** Logistic regression (L2, C = 0.63) inside a scikit-learn pipeline: standardised numeric features + one-hot categorical features. Saved as `models/churn_model.joblib`. Score new data with `python -m churn.predict` (see README).

**Data.** 7,043 customers (IBM sample dataset). 80/20 stratified split: 5,634 train, 1,409 test. 23 input features (see `data/DATA_DICTIONARY.md`).

**Selection.** Four initial candidates were compared with 5-fold cross-validation on the training set (baseline, logistic regression, random forest, gradient boosting); their *untuned* scores are in `reports/tables/model_comparison_cv.csv`. Logistic regression and gradient boosting were then tuned with randomized search using PR-AUC. The tuned comparison in `notebooks/03_modeling.ipynb` gave gradient boosting 0.6613 PR-AUC versus 0.6595 for logistic regression. The selection rule was set before evaluating the held-out test set: choose the best cross-validated PR-AUC, but prefer the simpler model when scores are within 0.005. Since the tuned models differ by only 0.0018, the simpler and more explainable logistic regression was selected. The held-out test results below evaluate that selected tuned model.

## Performance (held-out test set, used once)
| Metric | Value |
|---|---|
| ROC-AUC | 0.842 (95% bootstrap interval 0.819 to 0.864) |
| PR-AUC | 0.636 (95% interval 0.585 to 0.685); base rate 0.265 |
| Brier score | 0.138 (baseline 0.195) |
| Precision / recall at 0.5 | 0.66 / 0.55 |
| Top 20% of customers by score | contain 50.5% of churners |
| Top 40% of customers by score | contain 77.8% of churners |

Calibration: predicted probabilities match observed churn rates closely (see `reports/figures/07_model_curves.png`; out-of-fold average probability for the High tier 0.645 vs 0.657 observed).

## Decision threshold
0.27, chosen to maximise net campaign value under the assumptions in `src/churn/config.py` ($50 per offer, 30% of would-be churners retained, 12 months of revenue per saved customer), selected on out-of-fold training predictions and then applied to the test set. Change the assumptions and re-run to get a different threshold.

## Fairness and safety checks
- Gender: no meaningful difference in AUC (0.839 vs 0.846) or flag rate (40.5% vs 40.6%).
- Senior citizens: flagged much more often (67.6% vs 35.5%), in line with their higher actual churn (44.1% vs 23.3%), but the model ranks them less accurately (AUC 0.786 vs 0.842). Use scores for this group to trigger supportive outreach reviewed by a person.
- Gender is a model input but has no measurable effect; it can be dropped without loss if policy requires.

## Limitations
- One snapshot with no dates: no time-based validation, no survival analysis, and the model cannot say *when* a customer will leave.
- "Churn" means left in the last month; the label window is not documented in the source.
- Associations are not causes. The model shows who is at risk, not what would keep them. Causal claims need an A/B test.
- Sample data from a fictional company: performance on a real customer base must be re-measured.
- The business value depends on assumptions (offer cost, success rate) that this data cannot validate.

## Monitoring suggestions
Track monthly ROC-AUC on newly labelled customers, the share of customers in each risk tier, and calibration. Retrain when AUC falls by more than 0.03 or the tier mix shifts markedly.
