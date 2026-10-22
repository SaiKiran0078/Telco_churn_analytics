# Power BI report: guide

`powerbi/Telco Churn Report.pbip` is a Power BI Project (PBIR report + TMDL semantic model). It reads this repository's own files, so there is nothing to download.

## Open it
1. **Power BI Desktop** (Windows). If **File > Options > Preview features** lists *Power BI Project (.pbip) save option* and *Store reports using enhanced metadata format (PBIR)*, tick them and restart.
2. Clone or download this repository.
3. **Point the report at your copy** (one time). Power Query cannot use relative paths, so the report has a Text parameter `RepoRoot` that must hold the full path of this folder:
   - Python: `python scripts/init.py`
   - Windows without Python: `scripts\init.cmd`
   - By hand: open the `.pbip`, **Home > Transform data > Edit parameters**, set `RepoRoot` (for example `D:\work\telco-churn-analytics`) > OK > Apply.
4. Open `powerbi/Telco Churn Report.pbip` and click **Refresh**. 7,043 customers load.
5. Optional: **File > Save as** and pick **.pbix** for a single shareable file.
6. Before committing changes made on your machine: `python scripts/init.py --reset` so your local path is not stored in the repo.

The report reads `data/raw/Telco-Customer-Churn.csv` (and cleans it in Power Query with the same rules as the Python pipeline), plus three result tables from `reports/tables/` (`customer_risk_scores.csv`, `decile_table.csv`, `permutation_importance.csv`). If `reports/tables/` is empty, run `python scripts/run_all.py` first.

## Pages
| Page | Questions it answers |
|---|---|
| 1 Executive overview | How many customers, what churn rate, how much monthly revenue is lost; churn by contract, internet service, tenure, payment method; four auto-written insight lines |
| 2 Why customers leave | Churn by tenure and contract, protection services held, charge band, seniors, dependents, paperless billing; charge of churned vs retained |
| 3 Revenue at risk and segments | MRR lost, annualised loss, share per segment, segment table with recommended action, revenue lost by contract, internet, payment |
| 4 Risk model and call list | Model quality (ROC-AUC, PR-AUC, precision, recall), actual churn by risk tier, decile lift and cumulative capture, feature importance, call list of active High-risk customers |
| 5 Retention ROI simulator | Slicers for offer cost, success rate, months of revenue kept and risk threshold; contacted, saves, cost, revenue retained, net value, break-even success rate; three strategies compared; net value by threshold and by success rate |

Slicers on pages 1 to 4 are synchronised (contract, internet service, payment method, tenure, senior citizen). Click a bar to cross-filter. Page 4's model-quality cards and decile/feature charts show test-set results from Python and do not change with slicers.

## Numbers to check (no filters)
- 7,043 customers, 1,869 churned, churn rate 26.5%, MRR $456,117, MRR lost $139,131 (30.5%).
- Month-to-month: 55% of customers, 88.6% of churners; two-year contracts churn at 2.8%.
- Internet customers: churn 56.7% with no protection service, 5.3% with all four.
- Call list: 534 active customers in the High tier, $42,668 monthly revenue.
- Simulator defaults ($50 per offer, 30% success, 12 months, threshold 27%): 2,872 contacted, net value $270,221, break-even success rate 10.4%.

## Simulator: how it differs from the report in PROJECT_REPORT.md
The Python campaign figures ($36.9k per 1,000 customers) use the 1,409-customer test set. The simulator applies the same formula (gain = success rate x monthly charge x months for each contacted true churner, cost = offer cost for each contact) to all 7,043 customers using out-of-fold scores, so totals are larger. The break-even success rate (10.4%) is the same in both.

## Design notes
- Churn is read from the `Churn` column (customers who left in the last month), so "revenue lost" is revenue already lost. The call list is built from customers still active.
- No Date table: the dataset has no dates, only tenure.
- `Churn Probability`, risk tier, segment and action come from `customer_risk_scores.csv` and are merged into `Customers` in Power Query (left join on customer ID).
- Model metrics on page 4 (ROC-AUC 0.8423 etc.) are constants copied from `reports/metrics.json`; rerunning the Python pipeline does not update them automatically.

## If something does not load
- *"The file path ... could not be found"*: `RepoRoot` is wrong. Run `python scripts/init.py --check`, then re-run init.
- *Parameter or column errors after you re-ran the Python pipeline*: the report expects the file layouts in `scripts/init.py` (`FILES`).
- The project files were validated against Microsoft's published schemas and the report structure was checked automatically. Schema validation does not guarantee that every visual or measure renders correctly in every Power BI Desktop version; if a refresh or visual fails, capture the exact error and check the `RepoRoot` parameter and source-file paths.

Full measure list: [POWERBI_MEASURES.md](POWERBI_MEASURES.md). Page previews: `docs/images/powerbi-page*-*.png` (rendered from the supplied five-page report PDF). The `powerbi-page*-layout.png` files are separate layout wireframes.
