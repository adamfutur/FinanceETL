import pytest
import pandas as pd
from src.transformation.cleaner import DataCleaner
from src.transformation.currency import CurrencyTransformer
from src.transformation.rfm import RFMSegmenter

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'InvoiceNo': ['1', '2', '3'],
        'StockCode': ['A', 'A', 'B'],
        'Description': ['Desc A', 'Desc A', 'Desc B'],
        'Quantity': [10, -5, 20],
        'InvoiceDate': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'UnitPrice': [10.0, 10.0, 5.0],
        'CustomerID': ['100', '100', '101'],
        'Country': ['UK', 'UK', 'USA']
    })

def test_cleaner_removes_negative_quantity(sample_data):
    cleaner = DataCleaner(sample_data)
    cleaned = cleaner.clean()
    assert (cleaned['Quantity'] > 0).all()
    assert len(cleaned) == 2  # Should drop the negative one

def test_currency_conversion(sample_data):
    # Use pre-cleaned data for this test
    df = sample_data[sample_data['Quantity'] > 0].copy()
    rates = {'USD': 1.5, 'EUR': 1.2}
    
    transformer = CurrencyTransformer(df, rates)
    result = transformer.transform()
    
    # Check Row 1: 10 * 10 = 100 GBP
    row1 = result.iloc[0]
    assert row1['Total_GBP'] == pytest.approx(100.0)
    assert row1['Total_USD'] == pytest.approx(150.0)  # 100 * 1.5

def test_rfm_segmentation():
    # Need at least 4 customers for q=4 binning
    now = pd.Timestamp.now()
    data = {
        'CustomerID': ['A', 'B', 'C', 'D'],
        'InvoiceDate': [now, now - pd.Timedelta(days=10), now - pd.Timedelta(days=50), now - pd.Timedelta(days=100)],
        'InvoiceNo': ['1', '2', '3', '4'],
        'Total_GBP': [1000, 500, 100, 10]
    }
    df = pd.DataFrame(data)
    
    rfm = RFMSegmenter(df)
    result = rfm.generate_segments()
    
    # Check that segments are assigned
    assert 'Customer_Segment' in result.columns
    assert 'RFM_Score' in result.columns

def test_fraud_detection():
    data = {
        'InvoiceNo': ['1', '2', '3'],
        'StockCode': ['P1', 'P1', 'P1'],
        'UnitPrice': [10.0, 10.0, 50.0], # 50 is an anomaly (Avg is ~23)
        'Quantity': [1, 1, 1],
        'Total_GBP': [10.0, 10.0, 5000.0], # 5000 is a huge outlier
        'InvoiceDate': pd.to_datetime(['2023-01-01', '2023-01-01', '2023-01-01']),
        'CustomerID': ['C1', 'C1', 'C1']
    }
    df = pd.DataFrame(data)
    
    from src.transformation.fraud import FraudDetector
    detector = FraudDetector(df)
    result = detector.detect()
    
    # Row 3 (Index 2) should be flagged as suspect
    assert result.iloc[2]['Is_Fraud_Suspect'] == True
    assert result.iloc[0]['Is_Fraud_Suspect'] == False
