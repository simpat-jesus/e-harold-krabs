import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://api:8000"  # Inside docker-compose network
# For local dev, use: API_URL = "http://localhost:8000"

st.set_page_config(page_title="Finance Dashboard", layout="wide")

st.title("💰 Finance Assistant Dashboard")

# ---------- Load Data ----------
@st.cache_data(ttl=60)
def fetch_summary():
    try:
        response = requests.get(f"{API_URL}/insights/summary")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"total_income": 0, "total_expenses": 0, "balance": 0, "transactions": 0}

@st.cache_data(ttl=60)
def fetch_categories():
    try:
        response = requests.get(f"{API_URL}/insights/categories")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

@st.cache_data(ttl=60)
def fetch_monthly():
    try:
        response = requests.get(f"{API_URL}/insights/monthly")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

summary = fetch_summary()
categories = fetch_categories()
monthly = fetch_monthly()

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${summary['total_income']:.2f}")
col2.metric("Total Expenses", f"${summary['total_expenses']:.2f}")
col3.metric("Balance", f"${summary['balance']:.2f}")

st.divider()

# ---------- Charts ----------
st.subheader("Spending by Category")

if categories:
    cat_df = pd.DataFrame(categories)
    fig = px.pie(cat_df, values="amount", names="category", title="Expenses by Category")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No expense data available yet. Upload some transactions!")

st.subheader("Monthly Trend")

if monthly:
    monthly_df = pd.DataFrame(monthly)
    fig2 = px.line(monthly_df, x="month", y="amount", 
                   title="Monthly Net Flow (Income - Expenses)")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No monthly data available yet. Upload some transactions!")

st.divider()
st.caption("⚡ Powered by FastAPI + Streamlit + Ollama/OpenAI")
