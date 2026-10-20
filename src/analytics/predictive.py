import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from loguru import logger
from datetime import timedelta

class SalesForecaster:
    def __init__(self, df):
        self.df = df
        self.model = LinearRegression()

    def forecast_revenue(self, days=30):
        """Forecasts daily revenue for the next N days"""
        logger.info(f"Generating AI revenue forecast for the next {days} days...")
        
        # Aggregate daily revenue
        daily_sales = self.df.groupby(self.df['InvoiceDate'].dt.date)['Total_GBP'].sum().reset_index()
        daily_sales.columns = ['ds', 'y']
        daily_sales['ds'] = pd.to_datetime(daily_sales['ds'])
        
        # Feature Engineering: Ordinal date
        daily_sales['ds_ordinal'] = daily_sales['ds'].apply(lambda x: x.toordinal())
        
        # Train model
        X = daily_sales[['ds_ordinal']]
        y = daily_sales['y']
        self.model.fit(X, y)
        
        # Predict future
        last_date = daily_sales['ds'].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
        future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
        
        preds = self.model.predict(future_ordinals)
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_revenue_gbp': preds.clip(min=0) # No negative revenue
        })
        
        logger.success("Sales forecast generated successfully.")
        return forecast_df

class ChurnPredictor:
    def __init__(self, rfm_df):
        self.rfm_df = rfm_df

    def identify_high_risk_customers(self):
        """Uses RFM scores to identify customers likely to stop buying"""
        logger.info("Analyzing customer churn risk...")
        
        # Ensure R, F, M are numeric
        for col in ['R', 'F', 'M']:
            self.rfm_df[col] = pd.to_numeric(self.rfm_df[col], errors='coerce')

        # Simple heuristic model
        self.rfm_df['Churn_Risk_Score'] = (
            (5 - self.rfm_df['R']) * 0.6 + 
            (5 - self.rfm_df['F']) * 0.4
        ).round(2)
        
        high_risk = self.rfm_df[self.rfm_df['Churn_Risk_Score'] >= 3.5].copy()
        logger.info(f"Identified {len(high_risk)} customers at high risk of churn.")
        return high_risk
