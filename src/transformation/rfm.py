import pandas as pd
from loguru import logger

class RFMSegmenter:
    def __init__(self, df):
        self.df = df.copy()

    def generate_segments(self):
        """
        Calculates RFM metrics per customer:
        - Recency: Days since last purchase
        - Frequency: Number of invoice transactions
        - Monetary: Total spend
        """
        # Ensure latest date is relative to the dataset
        snapshot_date = self.df['InvoiceDate'].max() + pd.Timedelta(days=1)
        
        # Aggregate data by CustomerID
        rfm = self.df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (snapshot_date - x.max()).days, # Recency
            'InvoiceNo': 'nunique',                                   # Frequency
            'Total_GBP': 'sum'                                        # Monetary
        }).reset_index()
        
        # Rename columns
        rfm.rename(columns={
            'InvoiceDate': 'Recency',
            'InvoiceNo': 'Frequency',
            'Total_GBP': 'Monetary'
        }, inplace=True)
        
        # Simple Scoring (Quantiles 1-4)
        # Using qcut with duplicate dropping to handle uneven distributions
        # Actually standard RFM: High Recency (days) = Bad score. High Freq/Mon = Good score.
        
        # Recency: Lower is better (4=Recent, 1=Old)
        r_labels = [4, 3, 2, 1]
        rfm['R_Score'] = pd.qcut(rfm['Recency'], q=4, labels=r_labels, duplicates='drop')
        
        # Frequency: Higher is better (1=Low, 4=High) 
        f_labels = [1, 2, 3, 4]
        # Many customers have only 1 purchase, qcut might fail without duplicates='drop'
        # Can use rank first to smooth it out
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=4, labels=f_labels)
        
        # Monetary: Higher is better
        m_labels = [1, 2, 3, 4]
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=4, labels=m_labels)
        
        # Convert to int for concatenation
        rfm['R'] = rfm['R_Score'].astype(str)
        rfm['F'] = rfm['F_Score'].astype(str)
        rfm['M'] = rfm['M_Score'].astype(str)
        
        # RFM Segment Concatenation
        rfm['RFM_Segment'] = rfm['R'] + rfm['F'] + rfm['M']
        rfm['RFM_Score'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)
        
        # Define Actionable Customer Segments
        def segment_customer(row):
            score = row['RFM_Score']
            r = int(row['R'])
            f = int(row['F'])
            m = int(row['M'])
            
            if score >= 11:
                return 'Best Customers'
            elif score >= 9:
                return 'Loyal Customers'
            elif f >= 4 and m >= 4:
                return 'Big Spenders'
            elif score >= 7:
                return 'Potential Loyalists'
            elif r <= 1:
                return 'Lost Customers'
            elif r <= 2:
                return 'At Risk'
            else:
                return 'Recent Customers'

        rfm['Customer_Segment'] = rfm.apply(segment_customer, axis=1)
        
        logger.info("RFM Segmentation complete.")
        return rfm
