import pandas as pd
import numpy as np
from loguru import logger

class FraudDetector:
    def __init__(self, df):
        self.df = df.copy()

    def detect(self):
        """
        Multi-layered Fraud Detection Simulation:
        1. Statistical Outliers (IQR Method) on Total Transaction Value.
        2. Product Price Anomalies (Compare UnitPrice to Product Mean).
        3. Velocity Check (High frequency of invoices per Customer per day).
        """
        logger.info("Starting Advanced Fraud Detection Analysis...")
        
        # 1. IQR Method for Transaction Value
        Q1 = self.df['Total_GBP'].quantile(0.25)
        Q3 = self.df['Total_GBP'].quantile(0.75)
        IQR = Q3 - Q1
        value_outlier_limit = Q3 + 3.0 * IQR # Stringent threshold
        
        # 2. Product Price Anomaly
        # Detect if an item is sold at > 200% of its usual average price (potential fat-finger or fraud)
        avg_prices = self.df.groupby('StockCode')['UnitPrice'].transform('mean')
        price_anomaly = self.df['UnitPrice'] > (avg_prices * 2.0)
        
        # 3. High Velocity 
        # Customers with more than 10 unique invoices in a single day
        self.df['date_only'] = self.df['InvoiceDate'].dt.date
        invoice_counts = self.df.groupby(['CustomerID', 'date_only'])['InvoiceNo'].transform('nunique')
        velocity_anomaly = invoice_counts > 10
        
        # Aggregate Flags
        value_anomaly = self.df['Total_GBP'] > value_outlier_limit
        
        self.df['Is_Fraud_Suspect'] = value_anomaly | price_anomaly | velocity_anomaly
        
        # Cleanup
        if 'date_only' in self.df.columns:
            self.df.drop(columns=['date_only'], inplace=True)
            
        suspects = self.df['Is_Fraud_Suspect'].sum()
        logger.info(f"Fraud Analysis Complete: Flagged {suspects} suspicious transactions.")
        logger.info(f" - Value Outliers (> {value_outlier_limit:.2f} GBP): {value_anomaly.sum()}")
        logger.info(f" - Price Anomalies: {price_anomaly.sum()}")
        logger.info(f" - High Velocity Invoices: {velocity_anomaly.sum()}")
        
        return self.df
