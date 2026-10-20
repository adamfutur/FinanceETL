-- Finance ETL Hub - BigQuery Star Schema DDL
-- This script uses standard SQL for BigQuery

-- Dimension: Date
CREATE OR REPLACE TABLE `your_project.finance_dw.dim_date` (
    date_key INT64,
    full_date DATE,
    day_name STRING,
    month_name STRING,
    month INT64,
    quarter INT64,
    year INT64,
    is_weekend BOOL
);

-- Dimension: Customer
CREATE OR REPLACE TABLE `your_project.finance_dw.dim_customer` (
    customer_key STRING,
    country STRING,
    rfm_segment STRING,
    rfm_score INT64,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOL
);

-- Dimension: Product
CREATE OR REPLACE TABLE `your_project.finance_dw.dim_product` (
    product_key STRING,
    description STRING,
    unit_price_gbp FLOAT64
);

-- Fact: Sales
CREATE OR REPLACE TABLE `your_project.finance_dw.fact_sales` (
    sales_id INT64,
    invoice_no STRING,
    invoice_date TIMESTAMP,
    customer_key STRING,
    product_key STRING,
    quantity INT64,
    unit_price FLOAT64,
    total_gbp FLOAT64,
    total_usd FLOAT64,
    total_eur FLOAT64,
    total_mad FLOAT64,
    is_fraud_suspect BOOL
)
PARTITION BY DATE(invoice_date);
