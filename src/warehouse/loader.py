from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger
from config.settings import settings
from src.warehouse.models import create_tables, DimCustomer, FactSales, DimProduct, DimDate
import pandas as pd
import sqlalchemy

class WarehouseLoader:
    def __init__(self):
        connection_string = f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        self.engine = create_engine(connection_string)
        self.session_factory = sessionmaker(bind=self.engine)

    def init_db(self):
        """Create tables if they don't exist"""
        logger.info("Initializing Data Warehouse Schema...")
        create_tables(self.engine)

    def load_dimensions(self, df, rfm_df=None):
        """
        Load DimProduct, DimCustomer, and DimDate dimension tables.
        """
        session = self.session_factory()
        try:
            # 1. DimDate (populate for the range in the dataset)
            self._load_dates(df['InvoiceDate'])

            # 2. DimProduct
            logger.info("Syncing DimProduct...")
            products = df[['StockCode', 'Description', 'UnitPrice']].drop_duplicates(subset=['StockCode']).copy()
            products.columns = ['product_key', 'description', 'unit_price_gbp']
            
            # Efficient check for new records only
            existing_products = pd.read_sql("SELECT product_key FROM dim_product", self.engine)['product_key'].tolist()
            new_products = products[~products['product_key'].isin(existing_products)]
            
            if not new_products.empty:
                new_products.to_sql('dim_product', self.engine, if_exists='append', index=False)
                logger.info(f"Inserted {len(new_products)} new products.")
            
            # 3. DimCustomer
            if rfm_df is not None:
                logger.info("Syncing DimCustomer with RFM profiles...")
                country_map = df[['CustomerID', 'Country']].drop_duplicates().set_index('CustomerID')['Country'].to_dict()
                
                customers_to_load = pd.DataFrame({
                    'customer_key': rfm_df['CustomerID'],
                    'country': rfm_df['CustomerID'].map(country_map).fillna('Unknown'),
                    'rfm_segment': rfm_df['Customer_Segment'],
                    'rfm_score': rfm_df['RFM_Score'],
                    'is_current': True,
                    'valid_from': pd.Timestamp.now()
                })
                
                # For a PFE project, we'll clear and reload customers to ensure latest RFM is there
                session.execute(sqlalchemy.text("DELETE FROM dim_customer"))
                customers_to_load.to_sql('dim_customer', self.engine, if_exists='append', index=False)
                logger.info(f"Refreshed {len(customers_to_load)} customer profiles.")

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading dimensions: {e}")
            raise
        finally:
            session.close()

    def _load_dates(self, date_col):
        """Populates the dim_date table based on range of dates in dataframe"""
        logger.info("Populating Date Dimension...")
        # Ensure column is datetime
        date_col = pd.to_datetime(date_col)
        min_date = date_col.min().date()
        max_date = date_col.max().date()
        
        date_range = pd.date_range(min_date, max_date)
        date_df = pd.DataFrame({'full_date': date_range})
        
        date_df['date_key'] = date_df['full_date'].dt.strftime('%Y%m%d').astype(int)
        date_df['day_name'] = date_df['full_date'].dt.day_name()
        date_df['month_name'] = date_df['full_date'].dt.month_name()
        date_df['month'] = date_df['full_date'].dt.month
        date_df['quarter'] = date_df['full_date'].dt.quarter
        date_df['year'] = date_df['full_date'].dt.year
        date_df['is_weekend'] = date_df['full_date'].dt.dayofweek >= 5
        
        # Upsert logic for dates
        existing_dates = pd.read_sql("SELECT date_key FROM dim_date", self.engine)['date_key'].tolist()
        new_dates = date_df[~date_df['date_key'].isin(existing_dates)]
        
        if not new_dates.empty:
            new_dates.to_sql('dim_date', self.engine, if_exists='append', index=False)
            logger.info(f"Inserted {len(new_dates)} days into dim_date.")

    def load_facts(self, df):
        """Load FactSales"""
        logger.info("Loading FactSales...")
        # Prepare DataFrame
        facts = df.copy()
        
        # Mapping columns to DB schema
        facts_db = pd.DataFrame()
        facts_db['invoice_no'] = facts['InvoiceNo']
        facts_db['invoice_date'] = facts['InvoiceDate']
        facts_db['customer_key'] = facts['CustomerID']
        facts_db['product_key'] = facts['StockCode']
        facts_db['quantity'] = facts['Quantity']
        facts_db['unit_price'] = facts['UnitPrice']
        facts_db['total_gbp'] = facts['Total_GBP']
        facts_db['total_usd'] = facts['Total_USD']
        facts_db['total_eur'] = facts['Total_EUR']
        facts_db['total_mad'] = facts['Total_MAD']
        facts_db['is_fraud_suspect'] = facts.get('Is_Fraud_Suspect', False)
        
        # Bulk load
        facts_db.to_sql('fact_sales', self.engine, if_exists='append', index=False)
        logger.info(f"Loaded {len(facts_db)} sales records.")
