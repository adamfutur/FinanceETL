from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, MetaData, Date, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DimDate(Base):
    __tablename__ = 'dim_date'
    date_key = Column(Integer, primary_key=True)  # YYYYMMDD
    full_date = Column(Date)
    day_name = Column(String(20))
    month_name = Column(String(20))
    month = Column(Integer)
    quarter = Column(Integer)
    year = Column(Integer)
    is_weekend = Column(Boolean)

class DimCustomer(Base):
    __tablename__ = 'dim_customer'
    customer_key = Column(String(50), primary_key=True) # CustomerID
    country = Column(String(100))
    rfm_segment = Column(String(50)) # Champion, Loyal, etc.
    rfm_score = Column(Integer)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    is_current = Column(Boolean)

class DimProduct(Base):
    __tablename__ = 'dim_product'
    product_key = Column(String(50), primary_key=True) # StockCode
    description = Column(String(255))
    unit_price_gbp = Column(Float)

class FactSales(Base):
    __tablename__ = 'fact_sales'
    sales_id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_no = Column(String(50))
    invoice_date = Column(DateTime)
    customer_key = Column(String(50)) # FK
    product_key = Column(String(50))  # FK
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_gbp = Column(Float)
    total_usd = Column(Float)
    total_eur = Column(Float)
    total_mad = Column(Float)
    is_fraud_suspect = Column(Boolean)

def create_tables(engine):
    Base.metadata.create_all(engine)
