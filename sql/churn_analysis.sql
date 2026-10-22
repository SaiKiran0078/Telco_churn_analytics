-- Telco Customer Churn Analysis
-- I imported the CSV into the TelcoChurn database. These queries help me
-- check the data and look at the main reasons customers are leaving.
-- Run the sections one at a time and check the results as you go.

USE TelcoChurn;
GO

-- Check that the imported table is there.
SELECT
    CASE WHEN OBJECT_ID('dbo.TelcoChurn', 'U') IS NOT NULL
         THEN 'Table exists'
         ELSE 'Table not found'
    END AS table_status;
GO

-- Check the number of rows and preview a few records.
SELECT COUNT(*) AS total_customers
FROM dbo.TelcoChurn;
GO

SELECT TOP (10) *
FROM dbo.TelcoChurn;
GO


-- 1. Overall churn
-- This gives me a starting point before looking at customer groups.
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    CAST(100.0 * SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0) AS DECIMAL(6, 2)) AS churn_rate_pct,
    CAST(SUM(TRY_CONVERT(DECIMAL(10, 2), MonthlyCharges)) AS DECIMAL(18, 2)) AS total_monthly_charges,
    CAST(SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes'
                  THEN TRY_CONVERT(DECIMAL(10, 2), MonthlyCharges)
                  ELSE 0 END) AS DECIMAL(18, 2)) AS monthly_charges_from_churned_customers
FROM dbo.TelcoChurn;
GO


-- 2. Churn by contract
-- I want to see whether customers on month-to-month contracts leave more often.
SELECT
    Contract,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    CAST(100.0 * SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0) AS DECIMAL(6, 2)) AS churn_rate_pct
FROM dbo.TelcoChurn
GROUP BY Contract
ORDER BY churn_rate_pct DESC;
GO


-- 3. Churn by tenure
-- Grouping tenure makes it easier to see when customers tend to leave.
SELECT
    CASE
        WHEN TRY_CONVERT(INT, tenure) <= 6 THEN '0-6 months'
        WHEN TRY_CONVERT(INT, tenure) <= 12 THEN '7-12 months'
        WHEN TRY_CONVERT(INT, tenure) <= 24 THEN '13-24 months'
        WHEN TRY_CONVERT(INT, tenure) <= 48 THEN '25-48 months'
        ELSE '49-72 months'
    END AS tenure_group,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    CAST(100.0 * SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0) AS DECIMAL(6, 2)) AS churn_rate_pct
FROM dbo.TelcoChurn
GROUP BY
    CASE
        WHEN TRY_CONVERT(INT, tenure) <= 6 THEN '0-6 months'
        WHEN TRY_CONVERT(INT, tenure) <= 12 THEN '7-12 months'
        WHEN TRY_CONVERT(INT, tenure) <= 24 THEN '13-24 months'
        WHEN TRY_CONVERT(INT, tenure) <= 48 THEN '25-48 months'
        ELSE '49-72 months'
    END
ORDER BY tenure_group;
GO


-- 4. Churn by internet service
-- Compare customers using fiber optic, DSL, or no internet service.
SELECT
    InternetService,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    CAST(100.0 * SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0) AS DECIMAL(6, 2)) AS churn_rate_pct
FROM dbo.TelcoChurn
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;
GO


-- 5. Monthly charges from customers who churned
-- This is an estimate based on their monthly charges, not confirmed future loss.
SELECT
    Contract,
    COUNT(*) AS churned_customers,
    CAST(SUM(TRY_CONVERT(DECIMAL(10, 2), MonthlyCharges)) AS DECIMAL(18, 2)) AS monthly_charges_at_risk
FROM dbo.TelcoChurn
WHERE LTRIM(RTRIM(Churn)) = 'Yes'
GROUP BY Contract
ORDER BY monthly_charges_at_risk DESC;
GO


-- 6. Payment method and churn
-- Check whether churn rates differ across payment methods.
SELECT
    PaymentMethod,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    CAST(100.0 * SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0) AS DECIMAL(6, 2)) AS churn_rate_pct
FROM dbo.TelcoChurn
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;
GO


-- 7. Protective services
-- Count security, backup, device protection, and tech support for customers
-- who have internet service. Then compare churn across those groups.
SELECT
    protective_services,
    COUNT(*) AS total_customers,
    SUM(ChurnFlag) AS churned_customers,
    CAST(100.0 * AVG(CAST(ChurnFlag AS DECIMAL(10, 4))) AS DECIMAL(6, 2)) AS churn_rate_pct
FROM
(
    SELECT
        CASE WHEN LTRIM(RTRIM(OnlineSecurity)) = 'Yes' THEN 1 ELSE 0 END
      + CASE WHEN LTRIM(RTRIM(OnlineBackup)) = 'Yes' THEN 1 ELSE 0 END
      + CASE WHEN LTRIM(RTRIM(DeviceProtection)) = 'Yes' THEN 1 ELSE 0 END
      + CASE WHEN LTRIM(RTRIM(TechSupport)) = 'Yes' THEN 1 ELSE 0 END AS protective_services,
        CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END AS ChurnFlag
    FROM dbo.TelcoChurn
    WHERE LTRIM(RTRIM(InternetService)) <> 'No'
) AS service_summary
GROUP BY protective_services
ORDER BY protective_services;
GO


-- 8. One customer group worth a closer look
-- These customers have month-to-month contracts, fiber internet, and no
-- online security or tech support. Compare their churn rate with the overall rate.
SELECT
    COUNT(*) AS customers_in_group,
    SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    CAST(100.0 * SUM(CASE WHEN LTRIM(RTRIM(Churn)) = 'Yes' THEN 1 ELSE 0 END)
         / NULLIF(COUNT(*), 0) AS DECIMAL(6, 2)) AS churn_rate_pct,
    CAST(SUM(TRY_CONVERT(DECIMAL(10, 2), MonthlyCharges)) AS DECIMAL(18, 2)) AS total_monthly_charges
FROM dbo.TelcoChurn
WHERE LTRIM(RTRIM(Contract)) = 'Month-to-month'
  AND LTRIM(RTRIM(InternetService)) = 'Fiber optic'
  AND LTRIM(RTRIM(OnlineSecurity)) = 'No'
  AND LTRIM(RTRIM(TechSupport)) = 'No';
GO
