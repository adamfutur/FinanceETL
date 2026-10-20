-- Finance ETL Hub - Star Schema DDL
-- Generated for PostgreSQL

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE,
    day_name VARCHAR(20),
    month_name VARCHAR(20),
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN
);

-- Dimension: Customer (SCD Type 2 Ready)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key VARCHAR(50) PRIMARY KEY,
    country VARCHAR(100),
    rfm_segment VARCHAR(50),
    rfm_score INTEGER,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN
);

-- Dimension: Product
CREATE TABLE IF NOT EXISTS dim_product (
    product_key VARCHAR(50) PRIMARY KEY,
    description VARCHAR(255),
    unit_price_gbp FLOAT
);

-- Fact: Sales
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50),
    invoice_date TIMESTAMP,
    customer_key VARCHAR(50),
    product_key VARCHAR(50),
    quantity INTEGER,
    unit_price FLOAT,
    total_gbp FLOAT,
    total_usd FLOAT,
    total_eur FLOAT,
    total_mad FLOAT,
    is_fraud_suspect BOOLEAN
);
