import pandas as pd
from loguru import logger

class DataCleaner:
    def __init__(self, df):
        self.df = df.copy()

    def clean(self):
        """
        Performs data cleaning:
        1. Remove null InvoiceNo and CustomerID
        2. Remove negative/zero Quantity and UnitPrice
        3. Drop duplicates
        4. Standardize types
        """
        initial_count = len(self.df)
        
        # 1. Drop Rows with missing essential ID info
        self.df = self.df.dropna(subset=['InvoiceNo', 'CustomerID'])
        
        # 2. Filter out invalid financial records
        # Negative quantities usually represent returns, we'll exclude them for 
        # a "Sales Performance" analysis or handle them as separate 'Returns'
        # For this ETL, we focus on positive sales.
        self.df = self.df[self.df['Quantity'] > 0]
        self.df = self.df[self.df['UnitPrice'] > 0]
        
        # 3. Handle duplicates
        self.df = self.df.drop_duplicates()
        
        # 4. Standardize types and strings
        self.df['CustomerID'] = self.df['CustomerID'].astype(int).astype(str)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        
        # Strip whitespace and normalize case for categorical data
        for col in ['InvoiceNo', 'StockCode', 'Description', 'Country']:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
                if col in ['InvoiceNo', 'StockCode', 'Country']:
                    self.df[col] = self.df[col].str.upper()

        cleaned_count = len(self.df)
        logger.info(f"Cleaning complete. Rows: {initial_count} -> {cleaned_count} (Dropped {initial_count - cleaned_count})")
        
        return self.df

if __name__ == "__main__":
    # Test cleaning logic
    pass
