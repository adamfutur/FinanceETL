from google.cloud import bigquery, storage
from google.oauth2 import service_account
from loguru import logger
import pandas as pd
import os
from config.settings import settings

class GCPLoader:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("GCP_DATASET_ID", "finance_dw")
        self.bucket_name = os.getenv("GCP_BUCKET_NAME")
        self.credentials_path = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        
        if self.credentials_path and os.path.exists(self.credentials_path):
            self.credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
            self.bq_client = bigquery.Client(credentials=self.credentials, project=self.project_id)
            self.storage_client = storage.Client(credentials=self.credentials, project=self.project_id)
        else:
            self.bq_client = None
            self.storage_client = None
            logger.warning("GCP Credentials not found. Cloud features will be skipped.")

    def upload_to_gcs(self, local_path, destination_blob):
        """Uploads a file to a GCS bucket (Data Lake)"""
        if self.storage_client is None or not self.bucket_name:
            return False
            
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(destination_blob)
            blob.upload_from_filename(local_path)
            logger.success(f"File {local_path} uploaded to GCS: gs://{self.bucket_name}/{destination_blob}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to GCS: {e}")
            return False

    def upload_to_bigquery(self, df, table_name, if_exists='append'):
        """Uploads a dataframe to a BigQuery table (Data Warehouse)"""
        if self.bq_client is None:
            return False
            
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        try:
            job_config = bigquery.LoadJobConfig(
                write_disposition="WRITE_APPEND" if if_exists == 'append' else "WRITE_TRUNCATE",
            )
            
            job = self.bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result() 
            
            logger.success(f"Successfully uploaded {len(df)} rows to BigQuery: {table_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload to BigQuery: {e}")
            return False

    def load_star_schema(self, fact_df, rfm_df=None):
        """Orchestrates the cloud load"""
        if self.bq_client is None: return
        
        # 1. Load Facts
        fact_bq = fact_df.copy()
        fact_bq.columns = [c.lower() for c in fact_bq.columns]
        self.upload_to_bigquery(fact_bq, "fact_sales")
        
        # 2. Load Customers
        if rfm_df is not None:
            cust_bq = rfm_df.copy()
            cust_bq.columns = [c.lower() for c in cust_bq.columns]
            self.upload_to_bigquery(cust_bq, "dim_customer", if_exists='replace')
