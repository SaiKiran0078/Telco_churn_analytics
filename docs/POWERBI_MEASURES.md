# Power BI measure reference

Generated from the semantic model (`powerbi/Telco Churn Report.SemanticModel`). All measures live in table `_Measures`; hidden helpers are marked. Data tables: `Customers` (7,043 rows), `Decile Table` and `Feature Importance` (static results from the Python model), and disconnected helper tables for the simulator (`Strategy`, `Offer Cost`, `Success Rate`, `Horizon Months`, `Risk Threshold`, `Threshold Axis`, `Success Axis`).


## 1 Core KPIs

### Customer Count
Number of customers (one row each).

```dax
Customer Count =
COUNTROWS ( Customers )
```
Format: `#,0`

### Churned Customers
Customers who left in the last month.

```dax
Churned Customers =
SUM ( Customers[Churn Flag] )
```
Format: `#,0`

### Retained Customers
```dax
Retained Customers =
[Customer Count] - [Churned Customers]
```
Format: `#,0`

### Churn Rate
Share of customers who churned.

```dax
Churn Rate =
DIVIDE ( [Churned Customers], [Customer Count] )
```
Format: `0.0%`

### Retention Rate
```dax
Retention Rate =
1 - [Churn Rate]
```
Format: `0.0%`

### MRR
Monthly recurring revenue: sum of monthly charges.

```dax
MRR =
SUM ( Customers[Monthly Charges] )
```
Format: `$#,0`

### MRR Lost
Monthly revenue lost to churners.

```dax
MRR Lost =
CALCULATE ( SUM ( Customers[Monthly Charges] ), Customers[Churn Flag] = 1 )
```
Format: `$#,0`

### Share of MRR Lost
```dax
Share of MRR Lost =
DIVIDE ( [MRR Lost], [MRR] )
```
Format: `0.0%`

### Annualised Revenue Lost
```dax
Annualised Revenue Lost =
[MRR Lost] * 12
```
Format: `$#,0`

### MRR Retained
```dax
MRR Retained =
[MRR] - [MRR Lost]
```
Format: `$#,0`

### Average Monthly Charge
```dax
Average Monthly Charge =
AVERAGE ( Customers[Monthly Charges] )
```
Format: `$#,0.00`

### Avg Charge Churned
```dax
Avg Charge Churned =
CALCULATE ( AVERAGE ( Customers[Monthly Charges] ), Customers[Churn Flag] = 1 )
```
Format: `$#,0.00`

### Avg Charge Retained
```dax
Avg Charge Retained =
CALCULATE ( AVERAGE ( Customers[Monthly Charges] ), Customers[Churn Flag] = 0 )
```
Format: `$#,0.00`

### Average Tenure
```dax
Average Tenure =
AVERAGE ( Customers[Tenure Months] )
```
Format: `0.0`

### Median Tenure Churned
```dax
Median Tenure Churned =
CALCULATE ( MEDIAN ( Customers[Tenure Months] ), Customers[Churn Flag] = 1 )
```
Format: `0.0`

### Median Tenure Retained
```dax
Median Tenure Retained =
CALCULATE ( MEDIAN ( Customers[Tenure Months] ), Customers[Churn Flag] = 0 )
```
Format: `0.0`

### Lifetime Revenue Billed
```dax
Lifetime Revenue Billed =
SUM ( Customers[Total Charges] )
```
Format: `$#,0`

### Average Services Held
```dax
Average Services Held =
AVERAGE ( Customers[Num Services] )
```
Format: `0.0`


## 2 Compare and share

### Overall Churn Rate
Churn rate of all customers, ignoring every filter.

```dax
Overall Churn Rate =
CALCULATE ( [Churn Rate], REMOVEFILTERS ( Customers ) )
```
Format: `0.0%`

### Churn vs Overall (pp)
Percentage points above (+) or below (-) the overall churn rate.

```dax
Churn vs Overall (pp) =
[Churn Rate] - [Overall Churn Rate]
```
Format: `+0.0%;-0.0%;0.0%`

### Churn Lift
Churn rate as a multiple of the overall rate.

```dax
Churn Lift =
DIVIDE ( [Churn Rate], [Overall Churn Rate] )
```
Format: `0.00\x`

### Share of Customers
```dax
Share of Customers =
DIVIDE ( [Customer Count], CALCULATE ( [Customer Count], ALLSELECTED ( Customers ) ) )
```
Format: `0.0%`

### Share of Churners
```dax
Share of Churners =
DIVIDE ( [Churned Customers], CALCULATE ( [Churned Customers], ALLSELECTED ( Customers ) ) )
```
Format: `0.0%`

### Share of MRR Lost (of selection)
```dax
Share of MRR Lost (of selection) =
DIVIDE ( [MRR Lost], CALCULATE ( [MRR Lost], ALLSELECTED ( Customers ) ) )
```
Format: `0.0%`

### Share of MRR
```dax
Share of MRR =
DIVIDE ( [MRR], CALCULATE ( [MRR], ALLSELECTED ( Customers ) ) )
```
Format: `0.0%`


## 3 Contract and billing

### Month-to-month Customers
```dax
Month-to-month Customers =
CALCULATE ( [Customer Count], Customers[Contract] = "Month-to-month" )
```
Format: `#,0`

### Month-to-month Share of Customers
```dax
Month-to-month Share of Customers =
DIVIDE ( [Month-to-month Customers], [Customer Count] )
```
Format: `0.0%`

### Month-to-month Share of Churners
```dax
Month-to-month Share of Churners =
DIVIDE ( CALCULATE ( [Churned Customers], Customers[Contract] = "Month-to-month" ), [Churned Customers] )
```
Format: `0.0%`

### Churn Rate Month-to-month
```dax
Churn Rate Month-to-month =
CALCULATE ( [Churn Rate], Customers[Contract] = "Month-to-month" )
```
Format: `0.0%`

### Churn Rate Two-year
```dax
Churn Rate Two-year =
CALCULATE ( [Churn Rate], Customers[Contract] = "Two year" )
```
Format: `0.0%`

### Churn Rate Electronic Check
```dax
Churn Rate Electronic Check =
CALCULATE ( [Churn Rate], Customers[Payment Method] = "Electronic check" )
```
Format: `0.0%`

### Churn Rate Auto-pay
Bank transfer or credit card (automatic).

```dax
Churn Rate Auto-pay =
CALCULATE ( [Churn Rate], Customers[Payment Method] IN { "Bank transfer", "Credit card" } )
```
Format: `0.0%`

### Churn Rate Fiber
```dax
Churn Rate Fiber =
CALCULATE ( [Churn Rate], Customers[Internet Service] = "Fiber optic" )
```
Format: `0.0%`

### Churn Rate Paperless
```dax
Churn Rate Paperless =
CALCULATE ( [Churn Rate], Customers[Paperless Billing] = "Yes" )
```
Format: `0.0%`


## 4 Services and customers

### Churn Rate No Protection
Internet customers with none of security, backup, device protection, tech support.

```dax
Churn Rate No Protection =
CALCULATE ( [Churn Rate], Customers[Protection Services Held] = "0" )
```
Format: `0.0%`

### Churn Rate All Four Protection
```dax
Churn Rate All Four Protection =
CALCULATE ( [Churn Rate], Customers[Protection Services Held] = "4" )
```
Format: `0.0%`

### Churn Rate Senior
```dax
Churn Rate Senior =
CALCULATE ( [Churn Rate], Customers[Senior Citizen] = "Yes" )
```
Format: `0.0%`

### Churn Rate First Year
```dax
Churn Rate First Year =
CALCULATE ( [Churn Rate], Customers[Tenure Months] <= 12 )
```
Format: `0.0%`

### Churn Rate Over 4 Years
```dax
Churn Rate Over 4 Years =
CALCULATE ( [Churn Rate], Customers[Tenure Months] > 48 )
```
Format: `0.0%`

### Avg Services Churned
```dax
Avg Services Churned =
CALCULATE ( [Average Services Held], Customers[Churn Flag] = 1 )
```
Format: `0.0`

### Avg Services Retained
```dax
Avg Services Retained =
CALCULATE ( [Average Services Held], Customers[Churn Flag] = 0 )
```
Format: `0.0`


## 5 Segments and revenue at risk

### Top Segment by MRR Lost
Segment that loses the most monthly revenue.

```dax
Top Segment by MRR Lost =
MAXX ( TOPN ( 1, VALUES ( Customers[Segment] ), [MRR Lost] ), Customers[Segment] )
```

### Top Segment MRR Lost Share
```dax
Top Segment MRR Lost Share =
VAR s = [Top Segment by MRR Lost] RETURN DIVIDE ( CALCULATE ( [MRR Lost], Customers[Segment] = s ), [MRR Lost] )
```
Format: `0.0%`

### Highest Churn Segment
```dax
Highest Churn Segment =
MAXX ( TOPN ( 1, VALUES ( Customers[Segment] ), [Churn Rate] ), Customers[Segment] )
```

### Highest Segment Churn Rate
```dax
Highest Segment Churn Rate =
MAXX ( VALUES ( Customers[Segment] ), [Churn Rate] )
```
Format: `0.0%`

### Active High-Risk Customers
Customers still active whose model risk tier is High: the call list.

```dax
Active High-Risk Customers =
CALCULATE ( [Customer Count], Customers[Call List] = "Yes" )
```
Format: `#,0`

### Active High-Risk MRR
```dax
Active High-Risk MRR =
CALCULATE ( SUM ( Customers[Monthly Charges] ), Customers[Call List] = "Yes" )
```
Format: `$#,0`

### Expected MRR Loss (Active)
Sum over active customers of churn probability x monthly charge.

```dax
Expected MRR Loss (Active) =
SUMX ( FILTER ( Customers, Customers[Churn Flag] = 0 ), Customers[Churn Probability] * Customers[Monthly Charges] )
```
Format: `$#,0`

### MRR Lost per Churner
```dax
MRR Lost per Churner =
DIVIDE ( [MRR Lost], [Churned Customers] )
```
Format: `$#,0.00`


## 6 Risk model (from Python)

### Model ROC-AUC
Test-set ROC-AUC from reports/metrics.json (1,409 unseen customers).

```dax
Model ROC-AUC =
0.8423
```
Format: `0.000`

### Model PR-AUC
Test-set PR-AUC; the no-skill baseline equals the base rate 0.265.

```dax
Model PR-AUC =
0.6361
```
Format: `0.000`

### Model Precision
Share of contacted customers who would have churned, at threshold 0.27.

```dax
Model Precision =
0.6592
```
Format: `0.0%`

### Model Recall
Share of churners caught, at threshold 0.27.

```dax
Model Recall =
0.5535
```
Format: `0.0%`

### Model F1
```dax
Model F1 =
0.6017
```
Format: `0.000`

### Model Brier Score
```dax
Model Brier Score =
0.1379
```
Format: `0.000`

### Model Threshold
Contact threshold chosen from campaign economics.

```dax
Model Threshold =
0.27
```
Format: `0%`

### Avg Churn Probability
```dax
Avg Churn Probability =
AVERAGE ( Customers[Churn Probability] )
```
Format: `0.0%`

### Calibration Gap (pp)
Predicted minus actual churn rate; near zero means the scores behave like probabilities.

```dax
Calibration Gap (pp) =
[Avg Churn Probability] - [Churn Rate]
```
Format: `+0.0%;-0.0%;0.0%`

### Decile Churn Rate
```dax
Decile Churn Rate =
MAX ( 'Decile Table'[Churn Rate] )
```
Format: `0.0%`

### Decile Lift
```dax
Decile Lift =
MAX ( 'Decile Table'[Lift] )
```
Format: `0.00\x`

### Decile Cumulative Capture
```dax
Decile Cumulative Capture =
MAX ( 'Decile Table'[Cumulative Share of Churners] )
```
Format: `0%`

### Top 20% Capture
Share of churners found in the top 20% of customers by score (test set).

```dax
Top 20% Capture =
CALCULATE ( MAX ( 'Decile Table'[Cumulative Share of Churners] ), 'Decile Table'[Decile] = 2 )
```
Format: `0.0%`

### Top Decile Lift
```dax
Top Decile Lift =
CALCULATE ( MAX ( 'Decile Table'[Lift] ), 'Decile Table'[Decile] = 1 )
```
Format: `0.00\x`

### Feature AUC Drop
ROC-AUC lost when the feature is shuffled (permutation importance, test set).

```dax
Feature AUC Drop =
MAX ( 'Feature Importance'[AUC Drop] )
```
Format: `0.000`


## 7 Retention ROI simulator

### Offer Cost Selected
Cost of one retention offer (slicer; default $50).

```dax
Offer Cost Selected =
SELECTEDVALUE ( 'Offer Cost'[Offer Cost], 50 )
```
Format: `$#,0`

### Success Rate Selected
Share of would-be churners an offer keeps (slicer; default 30%).

```dax
Success Rate Selected =
SELECTEDVALUE ( 'Success Rate'[Success Rate], 0.3 )
```
Format: `0%`

### Horizon Months Selected
Months of revenue credited for a saved customer (default 12).

```dax
Horizon Months Selected =
SELECTEDVALUE ( 'Horizon Months'[Horizon Months], 12 )
```
Format: `0`

### Threshold Selected
Contact customers whose churn probability is at least this (default 27%).

```dax
Threshold Selected =
SELECTEDVALUE ( 'Risk Threshold'[Risk Threshold], 0.27 )
```
Format: `0%`

### Contacted (Model)
```dax
Contacted (Model) =
VAR t = [Threshold Selected] RETURN COUNTROWS ( FILTER ( Customers, Customers[Churn Probability] >= t ) )
```
Format: `#,0`

### Churners Reached (Model)
```dax
Churners Reached (Model) =
VAR t = [Threshold Selected] RETURN COUNTROWS ( FILTER ( Customers, Customers[Churn Probability] >= t && Customers[Churn Flag] = 1 ) )
```
Format: `#,0`

### Churner MRR Reached (Model) (hidden)
```dax
Churner MRR Reached (Model) =
VAR t = [Threshold Selected] RETURN SUMX ( FILTER ( Customers, Customers[Churn Probability] >= t && Customers[Churn Flag] = 1 ), Customers[Monthly Charges] )
```
Format: `$#,0`

### Customers Saved (Model)
```dax
Customers Saved (Model) =
[Churners Reached (Model)] * [Success Rate Selected]
```
Format: `#,0`

### Revenue Retained (Model)
```dax
Revenue Retained (Model) =
[Churner MRR Reached (Model)] * [Success Rate Selected] * [Horizon Months Selected]
```
Format: `$#,0`

### Campaign Cost (Model)
```dax
Campaign Cost (Model) =
[Contacted (Model)] * [Offer Cost Selected]
```
Format: `$#,0`

### Net Value (Model)
```dax
Net Value (Model) =
[Revenue Retained (Model)] - [Campaign Cost (Model)]
```
Format: `$#,0;-$#,0`

### ROI (Model)
```dax
ROI (Model) =
DIVIDE ( [Net Value (Model)], [Campaign Cost (Model)] )
```
Format: `0%;-0%`

### Break-even Success Rate (Model)
Offer success rate at which the model-targeted campaign just pays for itself.

```dax
Break-even Success Rate (Model) =
DIVIDE ( [Campaign Cost (Model)], [Churner MRR Reached (Model)] * [Horizon Months Selected] )
```
Format: `0.0%`

### Contacted (Everyone) (hidden)
```dax
Contacted (Everyone) =
COUNTROWS ( Customers )
```
Format: `#,0`

### Churners Reached (Everyone) (hidden)
```dax
Churners Reached (Everyone) =
[Churned Customers]
```
Format: `#,0`

### Revenue Retained (Everyone) (hidden)
```dax
Revenue Retained (Everyone) =
[MRR Lost] * [Success Rate Selected] * [Horizon Months Selected]
```
Format: `$#,0`

### Campaign Cost (Everyone) (hidden)
```dax
Campaign Cost (Everyone) =
[Contacted (Everyone)] * [Offer Cost Selected]
```
Format: `$#,0`

### Net Value (Everyone) (hidden)
```dax
Net Value (Everyone) =
[Revenue Retained (Everyone)] - [Campaign Cost (Everyone)]
```
Format: `$#,0;-$#,0`

### Contacted (M2M) (hidden)
```dax
Contacted (M2M) =
CALCULATE ( COUNTROWS ( Customers ), Customers[Contract] = "Month-to-month" )
```
Format: `#,0`

### Churners Reached (M2M) (hidden)
```dax
Churners Reached (M2M) =
CALCULATE ( [Churned Customers], Customers[Contract] = "Month-to-month" )
```
Format: `#,0`

### Revenue Retained (M2M) (hidden)
```dax
Revenue Retained (M2M) =
CALCULATE ( [MRR Lost], Customers[Contract] = "Month-to-month" ) * [Success Rate Selected] * [Horizon Months Selected]
```
Format: `$#,0`

### Campaign Cost (M2M) (hidden)
```dax
Campaign Cost (M2M) =
[Contacted (M2M)] * [Offer Cost Selected]
```
Format: `$#,0`

### Net Value (M2M) (hidden)
```dax
Net Value (M2M) =
[Revenue Retained (M2M)] - [Campaign Cost (M2M)]
```
Format: `$#,0;-$#,0`

### Strategy Contacted
```dax
Strategy Contacted =
SWITCH ( SELECTEDVALUE ( Strategy[Strategy] ), "Contact everyone", [Contacted (Everyone)], "Contact all month-to-month", [Contacted (M2M)], "Model-targeted", [Contacted (Model)], BLANK () )
```
Format: `#,0`

### Strategy Churners Reached
```dax
Strategy Churners Reached =
SWITCH ( SELECTEDVALUE ( Strategy[Strategy] ), "Contact everyone", [Churners Reached (Everyone)], "Contact all month-to-month", [Churners Reached (M2M)], "Model-targeted", [Churners Reached (Model)], BLANK () )
```
Format: `#,0`

### Strategy Cost
```dax
Strategy Cost =
SWITCH ( SELECTEDVALUE ( Strategy[Strategy] ), "Contact everyone", [Campaign Cost (Everyone)], "Contact all month-to-month", [Campaign Cost (M2M)], "Model-targeted", [Campaign Cost (Model)], BLANK () )
```
Format: `$#,0`

### Strategy Revenue Retained
```dax
Strategy Revenue Retained =
SWITCH ( SELECTEDVALUE ( Strategy[Strategy] ), "Contact everyone", [Revenue Retained (Everyone)], "Contact all month-to-month", [Revenue Retained (M2M)], "Model-targeted", [Revenue Retained (Model)], BLANK () )
```
Format: `$#,0`

### Strategy Net Value
```dax
Strategy Net Value =
SWITCH ( SELECTEDVALUE ( Strategy[Strategy] ), "Contact everyone", [Net Value (Everyone)], "Contact all month-to-month", [Net Value (M2M)], "Model-targeted", [Net Value (Model)], BLANK () )
```
Format: `$#,0;-$#,0`

### Strategy Net per 1,000 Customers
```dax
Strategy Net per 1,000 Customers =
DIVIDE ( [Strategy Net Value], [Customer Count] ) * 1000
```
Format: `$#,0;-$#,0`

### Strategy Churners Reached %
```dax
Strategy Churners Reached % =
DIVIDE ( [Strategy Churners Reached], [Churned Customers] )
```
Format: `0%`

### Net Value at Axis Threshold
Net value of the model-targeted campaign at each contact threshold on the axis.

```dax
Net Value at Axis Threshold =
VAR t = MAX ( 'Threshold Axis'[Threshold Axis] ) VAR sel = FILTER ( Customers, Customers[Churn Probability] >= t ) RETURN SUMX ( FILTER ( sel, Customers[Churn Flag] = 1 ), Customers[Monthly Charges] ) * [Success Rate Selected] * [Horizon Months Selected] - COUNTROWS ( sel ) * [Offer Cost Selected]
```
Format: `$#,0;-$#,0`

### Net Value at Axis Success Rate
Net value of the model-targeted campaign at each offer success rate on the axis.

```dax
Net Value at Axis Success Rate =
[Churner MRR Reached (Model)] * MAX ( 'Success Axis'[Success Axis] ) * [Horizon Months Selected] - [Campaign Cost (Model)]
```
Format: `$#,0;-$#,0`


## 8 Narrative text

### Insight Contract
```dax
Insight Contract =
"Month-to-month contracts are " & FORMAT ( [Month-to-month Share of Customers], "0%" ) & " of customers but " & FORMAT ( [Month-to-month Share of Churners], "0%" ) & " of churners; churn is " & FORMAT ( [Churn Rate Month-to-month], "0%" ) & " versus " & FORMAT ( [Churn Rate Two-year], "0%" ) & " on two-year contracts."
```

### Insight Protection
```dax
Insight Protection =
"Internet customers with no protection service churn at " & FORMAT ( [Churn Rate No Protection], "0%" ) & "; with all four, only " & FORMAT ( [Churn Rate All Four Protection], "0%" ) & "."
```

### Insight Payment
```dax
Insight Payment =
"Electronic-check payers churn at " & FORMAT ( [Churn Rate Electronic Check], "0%" ) & " versus " & FORMAT ( [Churn Rate Auto-pay], "0%" ) & " for automatic payment (bank transfer or card)."
```

### Insight Tenure
```dax
Insight Tenure =
"The first year is the danger zone: " & FORMAT ( [Churn Rate First Year], "0%" ) & " churn in months 0-12 against " & FORMAT ( [Churn Rate Over 4 Years], "0%" ) & " after four years."
```

### Insight Revenue
```dax
Insight Revenue =
"Churners take " & FORMAT ( [MRR Lost], "$#,0" ) & " of monthly revenue (" & FORMAT ( [Share of MRR Lost], "0.0%" ) & "), about " & FORMAT ( [Annualised Revenue Lost], "$#,0" ) & " a year."
```

### Insight Segment
```dax
Insight Segment =
"Largest revenue leak: " & [Top Segment by MRR Lost] & " (" & FORMAT ( [Top Segment MRR Lost Share], "0%" ) & " of revenue lost)."
```

### Insight Model
```dax
Insight Model =
"The model ranks customers well (ROC-AUC " & FORMAT ( [Model ROC-AUC], "0.00" ) & "): the top 20% by score hold " & FORMAT ( [Top 20% Capture], "0%" ) & " of churners."
```

### Insight Call List
```dax
Insight Call List =
FORMAT ( [Active High-Risk Customers], "#,0" ) & " active customers are in the High risk tier, worth " & FORMAT ( [Active High-Risk MRR], "$#,0" ) & " a month: call them first."
```

### Insight Simulator
```dax
Insight Simulator =
"At " & FORMAT ( [Offer Cost Selected], "$#,0" ) & " per offer and a " & FORMAT ( [Success Rate Selected], "0%" ) & " success rate, the model-targeted campaign nets " & FORMAT ( [Net Value (Model)], "$#,0" ) & "; it breaks even at " & FORMAT ( [Break-even Success Rate (Model)], "0.0%" ) & "."
```


## 9 Formatting helpers

### Churn Colour (hidden)
```dax
Churn Colour =
IF ( [Churn Rate] > [Overall Churn Rate], "#B42323", "#0B6B0B" )
```
