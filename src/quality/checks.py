from loguru import logger
import pandas as pd

class QualityChecks:
    def __init__(self, df):
        self.df = df

    def run_checks(self):
        """
        Runs a suite of data quality checks.
        Returns True if critical checks pass, False otherwise.
        """
        logger.info("Running Advanced Data Quality Suite...")
        passed = True
        
        # 1. Null Check (Non-negotiable columns)
        critical_cols = ['InvoiceNo', 'CustomerID', 'StockCode', 'Total_GBP']
        for col in critical_cols:
            null_count = self.df[col].isnull().sum()
            if null_count > 0:
                logger.error(f"DQ Failure: Column '{col}' contains {null_count} nulls.")
                passed = False

        # 2. Uniqueness Check
        # Combination of InvoiceNo and StockCode should be unique in most cases
        # (Actually, there might be multiple lines for same stock code in one invoice?
        # Standard retail usually has one line per product per invoice. Let's check duplicates.)
        duplicates = self.df.duplicated(subset=['InvoiceNo', 'StockCode']).sum()
        if duplicates > 0:
            logger.warning(f"DQ Warning: Found {duplicates} duplicate product entries within invoices. This might be normal but warrants review.")
        
        # 3. Negative Value Check (Critical for Fact Table)
        if (self.df['Quantity'] <= 0).any():
            logger.error("DQ Failure: Found zero or negative quantities after cleaning!")
            passed = False
            
        if (self.df['Total_GBP'] <= 0).any():
            logger.error("DQ Failure: Found zero or negative revenue!")
            passed = False
            
        # 4. Date Sanity
        # Check for future dates
        future_dates = (self.df['InvoiceDate'] > pd.Timestamp.now()).sum()
        if future_dates > 0:
            logger.error(f"DQ Failure: Found {future_dates} records with future timestamps!")
            passed = False

        # 5. Currency Conversion integrity
        if 'Total_USD' in self.df.columns:
            if (self.df['Total_USD'] == 0).all() and (self.df['Total_GBP'] != 0).any():
                 logger.error("DQ Failure: Multi-currency conversion failed (detected columns with all zeros).")
                 passed = False

        if passed:
            logger.info("✅ All critical Data Quality Checks Passed.")
        else:
            logger.error("❌ Data Quality Suite Failed. Review logs for details.")
            
        return passed
