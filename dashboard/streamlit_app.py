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
                'summary': executor.submit(requests.get, f"{API_URL}/insights/summary", timeout=30),
                'categories': executor.submit(requests.get, f"{API_URL}/insights/categories", timeout=30),
                'monthly': executor.submit(requests.get, f"{API_URL}/insights/monthly", timeout=30),
                'transactions': executor.submit(requests.get, f"{API_URL}/transactions", timeout=30)
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
                'recurring': executor.submit(requests.get, f"{API_URL}/insights/recurring", timeout=30),
                'anomalies': executor.submit(requests.get, f"{API_URL}/insights/anomalies", timeout=30),
                'forecast': executor.submit(requests.get, f"{API_URL}/insights/forecast", timeout=45)
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
        st.plotly_chart(fig, width='stretch', key="categories_chart")
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
        st.plotly_chart(fig2, width='stretch', key="monthly_chart")
    else:
        st.info("No monthly data available yet.")

# Recent transactions preview
if transactions_data.get('transactions'):
    st.subheader("📋 Recent Transactions")
    recent_df = pd.DataFrame(transactions_data['transactions'][-10:])  # Last 10 transactions
    st.dataframe(
        recent_df[['date', 'description', 'amount', 'category']], 
        width='stretch',
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
            st.dataframe(rec_df, width='stretch', hide_index=True)
            
            if 'amount' in rec_df.columns:
                total_recurring = rec_df["amount"].sum()
                st.metric("Total Monthly Recurring", f"${total_recurring:.2f}")
        else:
            st.info("No recurring expenses detected yet.")
    
    with tab2:
        if anomalies:
            anom_df = pd.DataFrame(anomalies)
            st.dataframe(anom_df, width='stretch', hide_index=True)
            st.warning(f"Found {len(anomalies)} unusual transactions.")
        else:
            st.success("No anomalies detected.")
    
    with tab3:
        if forecast.get("forecast") and isinstance(forecast["forecast"], dict):
            forecast_data = forecast["forecast"]
            trends_data = forecast.get("trends", {})
            
            # Main forecast metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Next Month Expenses", 
                    f"${forecast_data.get('next_month_expenses', 0):.2f}",
                    delta=f"{trends_data.get('expense_change_pct', 0):.1f}%" if trends_data.get('expense_change_pct') else None
                )
            with col2:
                st.metric(
                    "Next Month Income", 
                    f"${forecast_data.get('next_month_income', 0):.2f}",
                    delta=f"{trends_data.get('income_change_pct', 0):.1f}%" if trends_data.get('income_change_pct') else None
                )
            with col3:
                net_amount = forecast_data.get('next_month_net', 0)
                st.metric(
                    "Net Balance", 
                    f"${net_amount:.2f}",
                    delta="Positive" if net_amount > 0 else "Negative"
                )
            with col4:
                confidence_lower = forecast_data.get('confidence_lower', 0)
                confidence_upper = forecast_data.get('confidence_upper', 0)
                st.metric(
                    "Confidence Range", 
                    f"${confidence_lower:.0f} - ${confidence_upper:.0f}"
                )
            
            # Trends information
            st.subheader("📈 Trends Analysis")
            col1, col2 = st.columns(2)
            with col1:
                expense_trend = trends_data.get('expense_trend', 'stable')
                trend_color = "🔴" if expense_trend == "increasing" else "🟢" if expense_trend == "decreasing" else "🟡"
                st.info(f"{trend_color} **Expense Trend**: {expense_trend.title()}")
            with col2:
                income_trend = trends_data.get('income_trend', 'stable')
                trend_color = "🟢" if income_trend == "increasing" else "🔴" if income_trend == "decreasing" else "🟡"
                st.info(f"{trend_color} **Income Trend**: {income_trend.title()}")
            
            # Category forecasts
            if forecast.get("category_forecasts"):
                st.subheader("📊 Category Forecasts")
                category_data = forecast["category_forecasts"]
                
                # Create a DataFrame for better display
                categories_df = pd.DataFrame([
                    {
                        "Category": category,
                        "Forecast": f"${data['forecast']:.2f}",
                        "Trend": data['trend'].title(),
                        "Monthly Avg": f"${data['avg_monthly']:.2f}"
                    }
                    for category, data in category_data.items()
                ])
                
                if not categories_df.empty:
                    st.dataframe(categories_df, width="stretch")
            
            # Historical context
            if forecast.get("historical_data"):
                hist_data = forecast["historical_data"]
                st.subheader("📈 Historical Context")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Avg Monthly Expenses", f"${hist_data.get('avg_monthly_expense', 0):.2f}")
                with col2:
                    st.metric("Avg Monthly Income", f"${hist_data.get('avg_monthly_income', 0):.2f}")
            
            # Method and message
            method = forecast.get("method", "unknown")
            message = forecast.get("message", "")
            st.success(f"✅ {message} (Method: {method.replace('_', ' ').title()})")
            
        else:
            st.info(forecast.get("message", "Unable to generate forecast"))

st.divider()

# ---------- Export Section ----------
@st.cache_data(ttl=300)
def fetch_export_data(format_type: str):
    """Fetch export data with caching."""
    try:
        response = requests.get(f"{API_URL}/export/{format_type}", timeout=30)
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
    if st.button("📄 Download CSV", width='stretch'):
        csv_data = fetch_export_data("csv")
        if csv_data:
            st.download_button(
                label="💾 Download CSV File",
                data=csv_data,
                file_name=f"transactions_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch'
            )
        else:
            st.error("No data available for export")

with export_col2:
    if st.button("📊 Download Excel", width='stretch'):
        excel_data = fetch_export_data("excel")
        if excel_data:
            st.download_button(
                label="💾 Download Excel File",
                data=excel_data,
                file_name=f"transactions_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch'
            )
        else:
            st.error("No data available for export")

# Auto-refresh option with 2-minute timer
st.divider()
col1, col2 = st.columns([3, 1])

with col1:
    auto_refresh = st.checkbox("🔄 Auto-refresh every 2 minutes", key="auto_refresh")

with col2:
    if st.button("🔄 Refresh Now", width='stretch'):
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
