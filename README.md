
# Finance Data Platform (ETL Hub)

A comprehensive, production-ready Data Engineering project simulating a Financial Data Platform. This repository includes an end-to-end ETL pipeline, Data Warehouse modeling, and dashboard integration.

## 🚀 Features

- **Data Ingestion**: Automated download and conversion of Online Retail dataset; Exchange Rate API integration.
- **CDC Simulation**: Logic to simulate Incremental Loads (Change Data Capture).
- **Transformation**: Data cleaning, Multi-currency conversion (GBP, USD, EUR, MAD), and Advanced Fraud Detection.
- **Advanced Analytics**: Statistical RFM (Recency, Frequency, Monetary) Customer Segmentation with actionable labels.
- **Fraud Engine**: Multi-layered analysis (IQR Outliers, Price Anomalies, and Velocity Checks).
- **Data Warehouse**: Star Schema design (FactSales, DimCustomer, etc.) with pre-aggregated SQL Views.
- **Dashboards**: Integrated Streamlit application for real-time KPI visualization.
- **Quality Assurance**: Automated Data Quality Suite with uniqueness and date range validation.
- **Deployment**: Dockerized Database, GCP-ready scripts, and local FX rate caching.

## 📂 Project Structure

```bash
FinanceETLHub/
├── config/              # Configuration & Logging
├── src/
│   ├── ingestion/       # Multi-Source Loader (supports directory scanning), FX API, CDC
│   ├── transformation/  # Advanced Cleaning, Currency, RFM, Fraud Engine
│   ├── warehouse/       # SQLAlchemy Models, Robust Loader
│   └── quality/         # Advanced DQ Suite
├── sql/                 # PostgreSQL & BigQuery DDL/Views
├── dashboards/          # Streamlit App & Power BI Docs
├── gcp/                 # GCP Deployment Docs
├── tests/               # Pytest Unit Tests
├── main.py              # Multi-mode Orchestrator (Full, CDC, Ingest, etc.)
└── Makefile             # Task Automation Shortcut
```

## 🛠️ Setup & Installation

1. **Clone & Setup**
   ```bash
   make setup
   ```

2. **Configure Environment**
   - Edit `.env` and add your `EXCHANGE_RATE_API_KEY`.

3. **Launch Infrastructure**
   ```bash
   make up
   ```

## ▶️ Usage

### Run Modern ETL (CDC Mode)
Simulates an initial load followed by an incremental batch:
```bash
make cdc
```

### Run Full ETL Pipeline
```bash
make etl
```

### Launch Insights Dashboard
```bash
make dashboard
```

### Run Quality Tests
```bash
make test
```

## 📊 Analytics
The platform provides deep insights into:
- **Revenue Performance**: Multi-currency valuation across borders.
- **Customer Health**: Identification of 'Best Customers' and 'At Risk' profiles.
- **Security**: Automated flagging of suspicious transaction patterns.

Connect Power BI/Looker to `localhost:5432` or use the built-in Streamlit app.

---

## ☁️ Advanced: Cloud Migration (GCP)
The platform is ready to scale to the cloud using **Google BigQuery**.

1. **Credentials**: Place your `service-account.json` in the root and update `.env`:
   ```bash
   GCP_PROJECT_ID=your-project-id
   GCP_SERVICE_ACCOUNT_JSON=service-account.json
   ```
2. **Schema**: Run the BigQuery DDL found in `sql/bigquery/init_schema_bq.sql`.
3. **Run**: The pipeline will automatically detect your credentials and mirror data to BigQuery during the `load` step.

---

## 🔄 Advanced: Orchestration (Apache Airflow)
Automate the daily execution of your pipeline.

1. **DAG Location**: The orchestration file is located at `dags/finance_etl_dag.py`.
2. **Setup**: Copy this file into your Airflow `dags/` folder.
3. **Workflow**:
   - `ingest_data` -> `transform_and_analyze` -> `load_to_data_warehouse`
   - Includes automatic retries and failure logging.
