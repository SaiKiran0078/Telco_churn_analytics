-- Telco churn: business questions answered in SQL (SQLite dialect; also valid in PostgreSQL with minor type tweaks).
-- Tables: customers (cleaned data, one row per customer), scores (model risk scores, one row per customer).
-- Run:  python scripts/run_sql.py   -> results are saved to reports/tables/sql_*.csv

-- name: 01_headline_kpis
-- Overall churn, customer counts and monthly charges. Aliases retain both the
-- project pipeline's names and the equivalent names used in the learning SQL.
SELECT COUNT(*) AS customers,
       COUNT(*) AS total_customers,
       SUM(ChurnFlag) AS churned,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(100.0 * AVG(ChurnFlag), 1) AS churn_rate_pct,
       ROUND(SUM(MonthlyCharges), 0) AS mrr,
       ROUND(SUM(MonthlyCharges), 0) AS total_monthly_charges,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 0) AS mrr_lost,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 0) AS monthly_charges_from_churned_customers,
       ROUND(100.0 * SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END) / NULLIF(SUM(MonthlyCharges), 0), 1) AS mrr_lost_pct,
       ROUND(100.0 * SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END) / NULLIF(SUM(MonthlyCharges), 0), 1) AS monthly_charges_at_risk_pct
FROM customers;

-- name: 02_churn_by_contract
-- Share of customers, churn rate and share of all churners per contract type (window function for the shares).
SELECT Contract,
       COUNT(*) AS customers,
       COUNT(*) AS total_customers,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_customers,
       ROUND(100.0 * AVG(ChurnFlag), 1) AS churn_rate_pct,
       ROUND(100.0 * SUM(ChurnFlag) / NULLIF(SUM(SUM(ChurnFlag)) OVER (), 0), 1) AS pct_of_all_churners
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- name: 03_tenure_cohorts
-- Churn by how long the customer has been with us.
WITH bucketed AS (
    SELECT *, CASE WHEN tenure <= 6  THEN '1) 0-6 months'
                   WHEN tenure <= 12 THEN '2) 7-12 months'
                   WHEN tenure <= 24 THEN '3) 13-24 months'
                   WHEN tenure <= 48 THEN '4) 25-48 months'
                   ELSE                   '5) 49-72 months' END AS tenure_bucket
    FROM customers)
SELECT tenure_bucket,
       COUNT(*) AS customers,
       COUNT(*) AS total_customers,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(100.0 * AVG(ChurnFlag), 1) AS churn_rate_pct,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 0) AS mrr_lost,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 0) AS monthly_charges_from_churned_customers
FROM bucketed GROUP BY tenure_bucket ORDER BY tenure_bucket;

-- name: 04_pareto_of_revenue_lost
-- Which internet/contract/payment combinations lose the most revenue? Cumulative share shows how concentrated the loss is.
WITH combos AS (
    SELECT InternetService, Contract, PaymentMethod,
           COUNT(*) AS customers, ROUND(100.0 * AVG(ChurnFlag), 1) AS churn_rate_pct,
           SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END) AS mrr_lost
    FROM customers GROUP BY InternetService, Contract, PaymentMethod HAVING COUNT(*) >= 30)
SELECT RANK() OVER (ORDER BY mrr_lost DESC) AS rnk, InternetService, Contract, PaymentMethod, customers, churn_rate_pct, ROUND(mrr_lost, 0) AS mrr_lost,
       ROUND(100.0 * SUM(mrr_lost) OVER (ORDER BY mrr_lost DESC ROWS UNBOUNDED PRECEDING) / SUM(mrr_lost) OVER (), 1) AS cumulative_pct_of_mrr_lost
FROM combos ORDER BY rnk LIMIT 10;

-- name: 05_services_and_churn
-- Do customers with more protective services (security, backup, device protection, tech support) churn less?
WITH s AS (
    SELECT *, (OnlineSecurity = 'Yes') + (OnlineBackup = 'Yes') + (DeviceProtection = 'Yes') + (TechSupport = 'Yes') AS protective_services
    FROM customers WHERE InternetService <> 'No')
SELECT protective_services,
       COUNT(*) AS customers,
       COUNT(*) AS total_customers,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(100.0 * AVG(ChurnFlag), 1) AS churn_rate_pct,
       ROUND(AVG(MonthlyCharges), 1) AS avg_monthly_charge
FROM s GROUP BY protective_services ORDER BY protective_services;

-- name: 06_highest_risk_group
-- The group a retention programme should call first: month-to-month, fiber, no security and no tech support.
SELECT COUNT(*) AS customers,
       COUNT(*) AS customers_in_group,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct_of_base,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(100.0 * AVG(ChurnFlag), 1) AS churn_rate_pct,
       ROUND(100.0 * SUM(ChurnFlag) / NULLIF((SELECT SUM(ChurnFlag) FROM customers), 0), 1) AS pct_of_all_churners,
       ROUND(SUM(MonthlyCharges), 0) AS total_monthly_charges,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 0) AS mrr_lost,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 0) AS monthly_charges_from_churned_customers
FROM customers
WHERE Contract = 'Month-to-month' AND InternetService = 'Fiber optic' AND TechSupport = 'No' AND OnlineSecurity = 'No';

-- name: 07_payment_by_contract
-- Does the electronic-check effect survive once contract type is held constant?
SELECT Contract, PaymentMethod, COUNT(*) AS customers, ROUND(100.0 * AVG(ChurnFlag), 1) AS churn_rate_pct
FROM customers GROUP BY Contract, PaymentMethod ORDER BY Contract, churn_rate_pct DESC;

-- name: 08_call_list_top_revenue_at_risk
-- Operational output: still-active customers in the High risk tier, ranked by monthly revenue (join model scores).
SELECT c.customerID, s.segment, c.Contract, c.tenure, c.MonthlyCharges, s.churn_probability, s.recommended_action
FROM customers c JOIN scores s USING (customerID)
WHERE s.risk_tier = 'High' AND c.ChurnFlag = 0
ORDER BY c.MonthlyCharges * s.churn_probability DESC LIMIT 15;

-- name: 00_source_table_check
-- SQLite equivalent of checking that the imported table exists.
SELECT CASE WHEN EXISTS (
           SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'customers'
       ) THEN 'Table exists' ELSE 'Table not found' END AS table_status;

-- name: 00_row_count
-- Count the loaded records before reviewing the summaries.
SELECT COUNT(*) AS total_customers FROM customers;

-- name: 00_preview_top_10
-- Sample records for a quick import/column check (SQLite equivalent of TOP 10).
SELECT * FROM customers LIMIT 10;

-- name: 09_churn_by_internet_service
-- Compare churn across fiber, DSL, and no-internet customers.
SELECT InternetService,
       COUNT(*) AS total_customers,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(100.0 * AVG(ChurnFlag), 2) AS churn_rate_pct
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;

-- name: 10_monthly_charges_from_churned_by_contract
-- Monthly charges associated with customers already labelled as churned; this is not a measured future revenue loss.
SELECT Contract,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges ELSE 0 END), 2) AS monthly_charges_at_risk
FROM customers
GROUP BY Contract
ORDER BY monthly_charges_at_risk DESC;

-- name: 11_churn_by_payment_method
-- The learning SQL's standalone payment-method comparison; query 07 additionally controls for contract.
SELECT PaymentMethod,
       COUNT(*) AS total_customers,
       SUM(ChurnFlag) AS churned_customers,
       ROUND(100.0 * AVG(ChurnFlag), 2) AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;
