
# Online Retail Data Analysis - Dashboard Guide

## 1. Power BI Setup

### Data Source
- Select **Get Data** -> **PostgreSQL Database**
- Server: `localhost` (or Docker IP)
- Database: `finance_db`
- User/Pass: `postgres`/`postgres`

### Data Modeling
- **Fact Table**: `fact_sales`
- **Dimension Tables**: `dim_customer`, `dim_product`, `dim_date`, `dim_country`
- **Relationships**: Create One-to-Many relationships from Dims to Fact on keys (e.g. `customer_key` -> `customer_key`)

### Proposed KPIs (Measures)
1. **Total Revenue (GBP)** = `SUM(fact_sales[total_gbp])`
2. **Total Revenue (USD)** = `SUM(fact_sales[total_usd])`
3. **Average Order Value** = `[Total Revenue] / DISTINCTCOUNT(fact_sales[invoice_no])`
4. **Active Customers** = `DISTINCTCOUNT(fact_sales[customer_key])`

### Visualizations
1. **Global Sales Map**: Map visual using `dim_country[Country]` and `[Total Revenue]`
2. **Monthly Revenue Trend**: Line chart with `dim_date[Year-Month]` on X-axis
3. **Top 10 Products**: Bar chart of `dim_product[Description]` by Revenue
4. **RFM Segmentation**: Pie chart using `dim_customer[rfm_segment_name]` counts
