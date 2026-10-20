import pandas as pd
from loguru import logger
import numpy as np

class CDCSimulator:
    """
    Simulates Change Data Capture (CDC) by partitioning the dataset 
    into 'Initial' and 'Incremental' batches based on InvoiceDate.
    """
    def __init__(self, df):
        self.df = df
        # Convert InvoiceDate to datetime if not already
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.min_date = self.df['InvoiceDate'].min()
        self.max_date = self.df['InvoiceDate'].max()

    def get_initial_load(self, split_ratio=0.8):
        """Returns the first 80% of data chronologically as initial load"""
        # Sort by date
        sorted_df = self.df.sort_values('InvoiceDate')
        split_idx = int(len(sorted_df) * split_ratio)
        initial_df = sorted_df.iloc[:split_idx].copy()
        
        # Add metadata for CDC simulation
        initial_df['cdc_operation'] = 'INSERT'
        initial_df['cdc_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Generated initial load batch with {len(initial_df)} records.")
        return initial_df

    def get_incremental_load(self, split_ratio=0.8):
        """Returns the remaining 20% of data as increment"""
        sorted_df = self.df.sort_values('InvoiceDate')
        split_idx = int(len(sorted_df) * split_ratio)
        incremental_df = sorted_df.iloc[split_idx:].copy()
        
        # Simulate some updates and deletes in the increment
        # (For simplicity in this PFE, we mostly treat them as new inserts)
        incremental_df['cdc_operation'] = 'INSERT'
        incremental_df['cdc_timestamp'] = pd.Timestamp.now()
        
        logger.info(f"Generated incremental batch with {len(incremental_df)} records.")
        return incremental_df

if __name__ == "__main__":
    # Test with dummy data
    data = {'InvoiceDate': pd.date_range(start='1/1/2021', periods=100), 'val': range(100)}
    df = pd.DataFrame(data)
    cdc = CDCSimulator(df)
    init = cdc.get_initial_load()
    inc = cdc.get_incremental_load()
