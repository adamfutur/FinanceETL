import argparse
import sys
from loguru import logger
from src.ingestion.csv_loader import CSVLoader
from src.ingestion.fx_api import FXFetcher
from src.ingestion.cdc_simulator import CDCSimulator
from src.transformation.cleaner import DataCleaner
from src.transformation.currency import CurrencyTransformer
from src.transformation.rfm import RFMSegmenter
from src.transformation.fraud import FraudDetector
from src.warehouse.loader import WarehouseLoader
from src.warehouse.gcp_loader import GCPLoader
from src.analytics.predictive import SalesForecaster, ChurnPredictor
from src.quality.checks import QualityChecks
from config.logging_config import setup_logging

def main():
    parser = argparse.ArgumentParser(description="FinanceETLHub - End-to-End ETL Pipeline")
    parser.add_argument('--step', type=str, choices=['ingest', 'transform', 'load', 'full', 'cdc', 'dashboard', 'predict'], default='full', help='ETL Step to run')
    args = parser.parse_args()

    if args.step == 'dashboard':
        import subprocess
        logger.info("Launching Dashboard...")
        subprocess.run(["streamlit", "run", "dashboards/app.py"])
        return

    logger.info(f"Starting ETL Pipeline in '{args.step}' mode...")

    # Shared state
    raw_df = None

    # --- Step 1: Ingestion ---
    if args.step in ['ingest', 'full', 'cdc']:
        logger.info(">>> Step 1: Data Ingestion")
        loader = CSVLoader()
        raw_df = loader.get_data()
        
        fx_fetcher = FXFetcher()
        rates = fx_fetcher.get_rates()
        
        if raw_df is None or rates is None:
            logger.critical("Ingestion failed. Exiting.")
            sys.exit(1)

        # Mirror Raw Data to Cloud (Data Lake)
        gcp_loader = GCPLoader()
        if gcp_loader.storage_client:
            logger.info(">>> Archiving raw data to Cloud Storage (Data Lake)")
            gcp_loader.upload_to_gcs("data/raw/online_retail.csv", "raw/online_retail.csv")

        # Handle CDC Simulation
        if args.step == 'cdc':
            logger.info(">>> Simulating Change Data Capture (CDC)")
            cdc = CDCSimulator(raw_df)
            initial_batch = cdc.get_initial_load()
            incremental_batch = cdc.get_incremental_load()
            
            # Process Initial Batch first
            logger.info("Processing Initial Batch...")
            process_data(initial_batch, rates, is_initial=True)
            
            # Process Incremental Batch
            logger.info("Processing Incremental Batch...")
            process_data(incremental_batch, rates, is_initial=False)
            logger.success("CDC Pipeline Simulation Completed!")
            return

    # --- Step 2 & 3: Standard Flow ---
    if args.step in ['transform', 'load', 'full', 'predict']:
        if raw_df is None:
            loader = CSVLoader()
            raw_df = loader.get_data()
            fx_fetcher = FXFetcher()
            rates = fx_fetcher.get_rates()
        
        # In predict mode, we just need to run transformation to get clean data
        # but we don't necessarily need to load to DB unless specified.
        # Let's run it and then trigger AI logic.
        processed_df, rfm_df = process_data(raw_df, rates, run_load=(args.step != 'predict'))

        if args.step == 'predict':
            logger.info(">>> Step 4: AI Predictive Analytics")
            forecaster = SalesForecaster(processed_df)
            forecast = forecaster.forecast_revenue(days=30)
            
            churn_risk = ChurnPredictor(rfm_df)
            risky_customers = churn_risk.identify_high_risk_customers()
            
            print("\n--- AI SALES FORECAST (Next 7 Days) ---")
            print(forecast.head(7))
            print("\n--- TOP CHURN RISK CUSTOMERS ---")
            print(risky_customers[['CustomerID', 'Customer_Segment', 'Churn_Risk_Score']].head(10))
            
            # Save predictions for Dashboard
            forecast.to_csv("data/processed/sales_forecast.csv", index=False)
            risky_customers.to_csv("data/processed/churn_risk.csv", index=False)
            logger.success("Predictive insights saved to data/processed/")

def process_data(df, rates, is_initial=True, run_load=True):
    """Encapsulates the transformation and loading logic"""
    # 1. Cleaning
    cleaner = DataCleaner(df)
    clean_df = cleaner.clean()
    
    # 2. Currency Calc
    transformer = CurrencyTransformer(clean_df, rates)
    processed_df = transformer.transform()
    
    # 3. RFM Analysis
    rfm = RFMSegmenter(processed_df)
    rfm_df = rfm.generate_segments()
    
    # 4. Fraud Detection
    fraud = FraudDetector(processed_df)
    processed_df = fraud.detect()
    
    # 5. Data Quality
    dq = QualityChecks(processed_df)
    if not dq.run_checks():
        logger.error("Stopping pipeline due to DQ failures.")
        sys.exit(1)

    # 6. Warehouse Load
    if run_load:
        logger.info(">>> Loading to Data Warehouse")
        dw_loader = WarehouseLoader()
        gcp_loader = GCPLoader()
        
        try:
            if is_initial:
                dw_loader.init_db()
            dw_loader.load_dimensions(processed_df, rfm_df)
            dw_loader.load_facts(processed_df)
            
            # Cloud Upload (GCP)
            if gcp_loader.bq_client:
                logger.info(">>> Uploading to Google Cloud BigQuery")
                gcp_loader.load_star_schema(processed_df, rfm_df)
                
            logger.success("Batch Processing Successful!")
        except Exception as e:
            logger.critical(f"Warehouse load failed: {e}")
            sys.exit(1)
    
    return processed_df, rfm_df

if __name__ == "__main__":
    main()
