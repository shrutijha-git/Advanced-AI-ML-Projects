
-- InsightFlow Analytics
-- Business Intelligence SQL Queries
-- Table: retail_transactions

-- 1. Total revenue
SELECT
    ROUND(SUM(Revenue), 2) AS TotalRevenue
FROM retail_transactions;


-- 2. Total unique orders
SELECT
    COUNT(DISTINCT InvoiceNo) AS TotalOrders
FROM retail_transactions;


-- 3. Average order value
SELECT
    ROUND(
        SUM(Revenue) /
        NULLIF(COUNT(DISTINCT InvoiceNo), 0),
        2
    ) AS AverageOrderValue
FROM retail_transactions;


-- 4. Monthly revenue
SELECT
    SUBSTR(InvoiceDate, 1, 7) AS Month,
    ROUND(SUM(Revenue), 2) AS Revenue
FROM retail_transactions
GROUP BY SUBSTR(InvoiceDate, 1, 7)
ORDER BY Month;


-- 5. Top countries by revenue
SELECT
    Country,
    ROUND(SUM(Revenue), 2) AS Revenue,
    COUNT(DISTINCT InvoiceNo) AS Orders
FROM retail_transactions
GROUP BY Country
ORDER BY Revenue DESC
LIMIT 10;


-- 6. Top products by revenue
SELECT
    Description,
    ROUND(SUM(Revenue), 2) AS Revenue,
    SUM(Quantity) AS UnitsSold
FROM retail_transactions
GROUP BY Description
ORDER BY Revenue DESC
LIMIT 10;


-- 7. Top customers by spending
SELECT
    CustomerID,
    ROUND(SUM(Revenue), 2) AS Revenue,
    COUNT(DISTINCT InvoiceNo) AS Orders
FROM retail_transactions
WHERE CustomerID IS NOT NULL
  AND CustomerID != ''
GROUP BY CustomerID
ORDER BY Revenue DESC
LIMIT 10;


-- 8. Daily sales performance
SELECT
    DATE(InvoiceDate) AS SalesDate,
    ROUND(SUM(Revenue), 2) AS Revenue,
    COUNT(DISTINCT InvoiceNo) AS Orders
FROM retail_transactions
GROUP BY DATE(InvoiceDate)
ORDER BY SalesDate;
