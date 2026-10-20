import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import plotly.express as px

# --- Config ---
st.set_page_config(page_title="Finance ETL Insights", layout="wide")

DB_URL = "postgresql://postgres:postgres@localhost:5432/finance_db"
engine = create_engine(DB_URL)

st.title("📊 Finance Data Platform - Insights")

# --- Load Data ---
@st.cache_data
def load_data(query):
    return pd.read_sql(query, engine)

try:
    # Key Metrics
    st.subheader("🚀 Key Performance Indicators")
    cols = st.columns(4)
    
    total_sales = load_data("SELECT SUM(total_gbp) FROM fact_sales").iloc[0,0] or 0
    total_orders = load_data("SELECT COUNT(DISTINCT invoice_no) FROM fact_sales").iloc[0,0] or 0
    total_custs = load_data("SELECT COUNT(DISTINCT customer_key) FROM dim_customer").iloc[0,0] or 0
    avg_order = total_sales / total_orders if total_orders > 0 else 0

    cols[0].metric("Total Revenue (GBP)", f"£{total_sales:,.2f}")
    cols[1].metric("Total Orders", f"{total_orders:,}")
    cols[2].metric("Total Customers", f"{total_custs:,}")
    cols[3].metric("Avg Order Value", f"£{avg_order:,.2f}")

    # Visuals
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🌍 Sales by Country")
        country_data = load_data("""
            SELECT country, SUM(total_gbp) as revenue 
            FROM fact_sales f 
            JOIN dim_customer c ON f.customer_key = c.customer_key 
            GROUP BY country ORDER BY revenue DESC LIMIT 10
        """)
        fig = px.pie(country_data, values='revenue', names='country', hole=.3)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🎯 Customer Segmentation (RFM)")
        rfm_data = load_data("SELECT rfm_segment, COUNT(*) as count FROM dim_customer GROUP BY rfm_segment")
        fig = px.bar(rfm_data, x='rfm_segment', y='count', color='rfm_segment', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # --- AI Predictions ---
    st.divider()
    st.subheader("🤖 AI Predictive Insights")
    t1, t2 = st.tabs(["📈 Sales Forecast", "⚠️ Churn Risk Analysis"])
    
    with t1:
        try:
            forecast_df = pd.read_csv("data/processed/sales_forecast.csv")
            st.write("30-Day Revenue Projection (GBP)")
            fig_fc = px.line(forecast_df, x='date', y='predicted_revenue_gbp', labels={'predicted_revenue_gbp': 'Predicted Revenue (£)'})
            st.plotly_chart(fig_fc, use_container_width=True)
        except FileNotFoundError:
            st.info("Run 'python main.py --step predict' to generate AI forecasts.")
        except Exception as e:
            st.error(f"Forecast error: {e}")
            
    with t2:
        try:
            churn_df = pd.read_csv("data/processed/churn_risk.csv")
            st.write("Identifying customers at risk of leaving:")
            st.dataframe(churn_df[['CustomerID', 'Customer_Segment', 'Churn_Risk_Score']].sort_values(by='Churn_Risk_Score', ascending=False).head(10), use_container_width=True)
            st.warning("Action needed: These customers haven't purchased in a while!")
        except FileNotFoundError:
            st.info("Run 'python main.py --step predict' to analyze churn risk.")
        except Exception as e:
            st.error(f"Churn analysis error: {e}")

except Exception as e:
    st.info("The Data Warehouse is currently empty or still being loaded. Please wait for the ETL pipeline to finish!")
    st.error(f"Error: {e}")
