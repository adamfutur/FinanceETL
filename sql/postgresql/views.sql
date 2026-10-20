-- Finance ETL Hub - Analytical Views
-- PostgreSQL

-- View: Sales Performance by Country
CREATE OR REPLACE VIEW v_sales_by_country AS
SELECT 
    c.country, 
    COUNT(DISTINCT f.invoice_no) as total_orders,
    SUM(f.total_gbp) as revenue_gbp,
    AVG(f.total_gbp) as avg_order_value_gbp
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.country
ORDER BY revenue_gbp DESC;

-- View: Customer RFM Profiles
CREATE OR REPLACE VIEW v_customer_profiles AS
SELECT 
    customer_key,
    country,
    rfm_segment,
    rfm_score
FROM dim_customer
WHERE is_current = TRUE;

-- View: Fraud Suspects Report
CREATE OR REPLACE VIEW v_fraud_report AS
SELECT 
    invoice_no, 
    invoice_date, 
    customer_key, 
    total_gbp, 
    is_fraud_suspect
FROM fact_sales
WHERE is_fraud_suspect = TRUE;
