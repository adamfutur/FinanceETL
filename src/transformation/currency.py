import pandas as pd
from loguru import logger

class CurrencyTransformer:
    def __init__(self, df, exchange_rates):
        """
        :param df: Cleaned DataFrame
        :param exchange_rates: Dict of rates { 'USD': 1.27, 'EUR': 1.16, ... }
        """
        self.df = df.copy()
        self.rates = exchange_rates

    def transform(self):
        """
        Calculates Total Revenue in GBP (base), USD, EUR, MAD
        """
        # Base Calculation: Total GBP
        self.df['Total_GBP'] = self.df['Quantity'] * self.df['UnitPrice']
        
        # Multi-currency conversion
        for currency, rate in self.rates.items():
            if currency == 'GBP':
                continue
            col_name = f'Total_{currency}'
            self.df[col_name] = self.df['Total_GBP'] * rate
            
        logger.info(f"Currency transformation applied for: {list(self.rates.keys())}")
        return self.df
