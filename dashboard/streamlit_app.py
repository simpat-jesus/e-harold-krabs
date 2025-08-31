import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
import time

API_URL = "http://api:8000"  # Inside docker-compose network
# For local dev, use: API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Finance Dashboard", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Optimize Streamlit performance
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    div.stButton > button:first-child {
        background-color: #0066cc;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("💰 Finance Dashboard")

# ---------- Optimized Data Loading ----------
@st.cache_data(ttl=300, show_spinner=False)  # Increased TTL to 5 minutes
def fetch_all_data():
    """Fetch all dashboard data in a single optimized call."""
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all requests concurrently
            futures = {
                'summary': executor.submit(requests.get, f"{API_URL}/insights/summary", timeout=10),
                'categories': executor.submit(requests.get, f"{API_URL}/insights/categories", timeout=10),
                'monthly': executor.submit(requests.get, f"{API_URL}/insights/monthly", timeout=10),
                'transactions': executor.submit(requests.get, f"{API_URL}/transactions", timeout=15)
            }
            
            # Collect results
            results = {}
            for key, future in futures.items():
                try:
                    response = future.result()
                    response.raise_for_status()
                    results[key] = response.json()
                except Exception as e:
                    st.error(f"Failed to load {key}: {str(e)}")
                    results[key] = _get_empty_data(key)
            
            return results
    except Exception as e:
        st.error(f"Failed to load dashboard data: {str(e)}")
        return _get_all_empty_data()

@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes
def fetch_advanced_data():
    """Fetch advanced analytics data only when needed."""
    try:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                'recurring': executor.submit(requests.get, f"{API_URL}/insights/recurring", timeout=15),
                'anomalies': executor.submit(requests.get, f"{API_URL}/insights/anomalies", timeout=15),
                'forecast': executor.submit(requests.get, f"{API_URL}/insights/forecast", timeout=20)
            }
            
            results = {}
            for key, future in futures.items():
                try:
                    response = future.result()
                    response.raise_for_status()
                    results[key] = response.json()
                except Exception as e:
                    results[key] = _get_empty_data(key)
            
            return results
    except Exception:
        return _get_all_empty_advanced_data()

def _get_empty_data(data_type: str) -> Any:
    """Return appropriate empty data structure."""
    empty_data = {
        'summary': {"total_income": 0, "total_expenses": 0, "balance": 0, "transactions": 0},
        'categories': [],
        'monthly': [],
        'transactions': {"transactions": [], "total": 0},
        'recurring': [],
        'anomalies': [],
        'forecast': {"forecast": None, "message": "Unable to fetch forecast"}
    }
    return empty_data.get(data_type, [])

def _get_all_empty_data() -> Dict[str, Any]:
    """Return all empty data structures."""
    return {
        'summary': _get_empty_data('summary'),
        'categories': _get_empty_data('categories'),
        'monthly': _get_empty_data('monthly'),
        'transactions': _get_empty_data('transactions')
    }

def _get_all_empty_advanced_data() -> Dict[str, Any]:
    """Return empty advanced data structures."""
    return {
        'recurring': _get_empty_data('recurring'),
        'anomalies': _get_empty_data('anomalies'),
        'forecast': _get_empty_data('forecast')
    }

# Load core data
with st.spinner("Loading dashboard..."):
    data = fetch_all_data()

summary = data['summary']
categories = data['categories']
monthly = data['monthly']
transactions_data = data['transactions']

# Core dashboard metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"${summary['total_income']:.2f}")
col2.metric("Total Expenses", f"${summary['total_expenses']:.2f}")
col3.metric("Balance", f"${summary['balance']:.2f}")
col4.metric("Transactions", summary['transactions'])

st.divider()

# ---------- Main Charts ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("💳 Spending by Category")
    if categories:
        cat_df = pd.DataFrame(categories)
        fig = px.pie(
            cat_df, 
            values="amount", 
            names="category", 
            title="Expenses by Category",
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True, key="categories_chart")
    else:
        st.info("No expense data available yet.")

with col2:
    st.subheader("📈 Monthly Trend")
    if monthly:
        monthly_df = pd.DataFrame(monthly)
        fig2 = px.line(
            monthly_df, 
            x="month", 
            y="amount", 
            title="Monthly Net Flow",
            markers=True
        )
        fig2.update_layout(
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig2, use_container_width=True, key="monthly_chart")
    else:
        st.info("No monthly data available yet.")

# Recent transactions preview
if transactions_data.get('transactions'):
    st.subheader("📋 Recent Transactions")
    recent_df = pd.DataFrame(transactions_data['transactions'][-10:])  # Last 10 transactions
    st.dataframe(
        recent_df[['date', 'description', 'amount', 'category']], 
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ---------- Advanced Analytics (Lazy Loaded) ----------
if st.checkbox("🔍 Show Advanced Analytics", key="show_advanced"):
    with st.spinner("Loading advanced analytics..."):
        advanced_data = fetch_advanced_data()
    
    recurring = advanced_data['recurring']
    anomalies = advanced_data['anomalies'] 
    forecast = advanced_data['forecast']
    
    # Use tabs for better organization
    tab1, tab2, tab3 = st.tabs(["🔄 Recurring Expenses", "🚨 Anomalies", "🔮 Forecast"])
    
    with tab1:
        if recurring:
            rec_df = pd.DataFrame(recurring)
            st.dataframe(rec_df, use_container_width=True, hide_index=True)
            
            if 'amount' in rec_df.columns:
                total_recurring = rec_df["amount"].sum()
                st.metric("Total Monthly Recurring", f"${total_recurring:.2f}")
        else:
            st.info("No recurring expenses detected yet.")
    
    with tab2:
        if anomalies:
            anom_df = pd.DataFrame(anomalies)
            st.dataframe(anom_df, use_container_width=True, hide_index=True)
            st.warning(f"Found {len(anomalies)} unusual transactions.")
        else:
            st.success("No anomalies detected.")
    
    with tab3:
        if forecast.get("forecast"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Next Month Forecast", f"${forecast['forecast']:.2f}")
            with col2:
                st.metric("Lower Bound", f"${forecast['confidence_lower']:.2f}")
            with col3:
                st.metric("Upper Bound", f"${forecast['confidence_upper']:.2f}")
            st.info(forecast.get("message", ""))
        else:
            st.info(forecast.get("message", "Unable to generate forecast"))

st.divider()

# ---------- Export Section ----------
@st.cache_data(ttl=300)
def fetch_export_data(format_type: str):
    """Fetch export data with caching."""
    try:
        response = requests.get(f"{API_URL}/export/{format_type}", timeout=15)
        response.raise_for_status()
        if format_type == "csv":
            return response.text
        else:  # excel
            return response.content
    except requests.RequestException:
        return None

st.subheader("📊 Export Data")
export_col1, export_col2 = st.columns(2)

with export_col1:
    if st.button("📄 Download CSV", use_container_width=True):
        csv_data = fetch_export_data("csv")
        if csv_data:
            st.download_button(
                label="💾 Download CSV File",
                data=csv_data,
                file_name=f"transactions_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.error("No data available for export")

with export_col2:
    if st.button("📊 Download Excel", use_container_width=True):
        excel_data = fetch_export_data("excel")
        if excel_data:
            st.download_button(
                label="💾 Download Excel File",
                data=excel_data,
                file_name=f"transactions_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("No data available for export")

# Auto-refresh option with 2-minute timer
st.divider()
col1, col2 = st.columns([3, 1])

with col1:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 2 minutes", key="auto_refresh")

with col2:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Auto-refresh implementation
if auto_refresh:
    # Initialize session state for timer
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    current_time = time.time()
    time_since_refresh = current_time - st.session_state.last_refresh
    
    # Check if 2 minutes (120 seconds) have passed
    if time_since_refresh >= 120:
        st.session_state.last_refresh = current_time
        st.cache_data.clear()
        st.rerun()
    else:
        # Show countdown timer
        remaining_seconds = int(120 - time_since_refresh)
        remaining_minutes = remaining_seconds // 60
        remaining_secs = remaining_seconds % 60
        
        if remaining_minutes > 0:
            st.info(f"⏱️ Next refresh in {remaining_minutes}m {remaining_secs}s")
        else:
            st.info(f"⏱️ Next refresh in {remaining_secs}s")
        
        # Use a small delay to update the timer without being too aggressive
        time.sleep(1)
        st.rerun()

st.divider()
st.caption("⚡ Finance Assistant | Optimized Dashboard v2.0")
