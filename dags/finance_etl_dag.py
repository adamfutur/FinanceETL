from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os

# Default arguments for the DAG
default_args = {
    'owner': 'finance_admin',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'finance_etl_hub_pipeline',
    default_args=default_args,
    description='End-to-end Finance ETL Pipeline from UCI to PostgreSQL & BigQuery',
    schedule_interval=timedelta(days=1),
    catchup=False
)

# Define tasks using the existing main.py logic
# Use BashOperator to leverage the robust orchestrator we built

t1_ingest = BashOperator(
    task_id='ingest_data',
    bash_command='python c:/Users/MSI/Desktop/FinanceETLHub/main.py --step ingest',
    dag=dag,
)

t2_transform = BashOperator(
    task_id='transform_and_analyze',
    bash_command='python c:/Users/MSI/Desktop/FinanceETLHub/main.py --step transform',
    dag=dag,
)

t3_load = BashOperator(
    task_id='load_to_data_warehouse',
    bash_command='python c:/Users/MSI/Desktop/FinanceETLHub/main.py --step load',
    dag=dag,
)

# Task sequence
t1_ingest >> t2_transform >> t3_load
