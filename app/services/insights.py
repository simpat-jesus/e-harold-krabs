import pandas as pd
from db.models import Transaction
from collections import defaultdict
from datetime import datetime, timedelta
from prophet import Prophet

def get_summary(db):
    results = db.query(Transaction).all()
    df = pd.DataFrame([{
        "date": t.date,
        "description": t.description,
        "amount": t.amount,
        "category": t.category
    } for t in results])

    total_expenses = df[df["amount"] < 0]["amount"].sum() if not df.empty else 0
    total_income = df[df["amount"] > 0]["amount"].sum() if not df.empty else 0
    balance = total_income + total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "transactions": len(df)
    }

def get_categories(db):
    results = db.query(Transaction).all()
    df = pd.DataFrame([{
        "category": t.category or "Uncategorized",
        "amount": t.amount
    } for t in results])

    if df.empty:
        return []

    # Group by category and sum amounts (only expenses for pie chart)
    expenses_df = df[df["amount"] < 0]
    grouped = expenses_df.groupby("category")["amount"].sum().abs().reset_index()
    grouped = grouped.sort_values("amount", ascending=False)

    return grouped.to_dict("records")

def get_monthly_trends(db):
    results = db.query(Transaction).all()
    df = pd.DataFrame([{
        "date": t.date,
        "amount": t.amount
    } for t in results])

    if df.empty:
        return []

    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly = df.groupby("month")["amount"].sum().reset_index()
    monthly = monthly.sort_values("month")

    return monthly.to_dict("records")

def detect_anomalies(db):
    """Detect outlier spends using statistical methods."""
    results = db.query(Transaction).filter(Transaction.amount < 0).all()
    df = pd.DataFrame([{
        "date": t.date,
        "description": t.description,
        "amount": t.amount,
        "category": t.category
    } for t in results])

    if len(df) < 10:  # Need minimum data for anomaly detection
        return []

    # Calculate statistical measures
    df["amount_abs"] = df["amount"].abs()

    # Method 1: Z-score based anomaly detection
    mean_amount = df["amount_abs"].mean()
    std_amount = df["amount_abs"].std()

    if std_amount == 0:  # All amounts are the same
        return []

    df["z_score"] = (df["amount_abs"] - mean_amount) / std_amount

    # Method 2: IQR based anomaly detection
    Q1 = df["amount_abs"].quantile(0.25)
    Q3 = df["amount_abs"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Find anomalies (either z-score > 3 or outside IQR bounds)
    anomalies = df[
        (df["z_score"] > 3) |
        (df["amount_abs"] < lower_bound) |
        (df["amount_abs"] > upper_bound)
    ].copy()

    # Sort by most anomalous (highest z-score)
    anomalies = anomalies.sort_values("z_score", ascending=False)

    return anomalies[[
        "date", "description", "amount", "category", "z_score"
    ]].to_dict("records")

def forecast_expenses(db):
    """Enhanced forecasting with multiple methods and better insights."""
    results = db.query(Transaction).all()
    df = pd.DataFrame([{
        "date": t.date,
        "amount": t.amount,
        "category": t.category or "Uncategorized"
    } for t in results])

    if len(df) < 10:  # Reduced minimum requirement
        return {
            "forecast": None, 
            "message": "Insufficient data for forecasting (need at least 10 transactions)",
            "method": "none"
        }

    # Convert to datetime and sort
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    
    # Separate income and expenses
    expenses_df = df[df["amount"] < 0].copy()
    income_df = df[df["amount"] > 0].copy()
    
    # Aggregate by month for trends
    df["month"] = df["date"].dt.to_period("M")
    monthly_data = df.groupby("month").agg({
        "amount": ["sum", "count"]
    }).round(2)
    monthly_data.columns = ["net_amount", "transaction_count"]
    monthly_data = monthly_data.reset_index()
    monthly_data["month"] = monthly_data["month"].astype(str)
    
    # Calculate expense and income trends separately
    monthly_expenses = expenses_df.groupby(expenses_df["date"].dt.to_period("M"))["amount"].sum().abs()
    monthly_income = income_df.groupby(income_df["date"].dt.to_period("M"))["amount"].sum()
    
    try:
        # Method 1: Simple trend-based forecast (fast and reliable)
        if len(monthly_expenses) >= 3:
            # Calculate trends for expenses
            expense_trend = _calculate_trend_forecast(monthly_expenses)
            income_trend = _calculate_trend_forecast(monthly_income) if len(monthly_income) >= 3 else {"forecast": 0, "trend": "stable"}
            
            # Category-based forecasting
            category_forecasts = _forecast_by_category(expenses_df)
            
            # Method 2: Seasonal adjustment
            seasonal_adjustment = _calculate_seasonal_adjustment(monthly_expenses)
            
            # Method 3: Prophet forecast (only if enough data and time permits)
            prophet_forecast = None
            if len(monthly_expenses) >= 6:
                try:
                    prophet_forecast = _prophet_forecast_optimized(monthly_expenses)
                except Exception:
                    pass  # Fall back to trend-based
            
            # Combine forecasts for final prediction
            next_month_expense = expense_trend["forecast"] * seasonal_adjustment
            next_month_income = income_trend["forecast"]
            next_month_net = next_month_income - next_month_expense
            
            # Calculate confidence based on historical variance
            expense_variance = monthly_expenses.var() if len(monthly_expenses) > 1 else 0
            confidence_range = expense_variance ** 0.5 * 1.96  # 95% confidence interval
            
            return {
                "forecast": {
                    "next_month_expenses": round(next_month_expense, 2),
                    "next_month_income": round(next_month_income, 2),
                    "next_month_net": round(next_month_net, 2),
                    "confidence_lower": round(next_month_expense - confidence_range, 2),
                    "confidence_upper": round(next_month_expense + confidence_range, 2)
                },
                "trends": {
                    "expense_trend": expense_trend["trend"],
                    "income_trend": income_trend["trend"],
                    "expense_change_pct": expense_trend.get("change_pct", 0),
                    "income_change_pct": income_trend.get("change_pct", 0)
                },
                "category_forecasts": category_forecasts,
                "historical_data": {
                    "monthly_expenses": {str(k): float(v) for k, v in monthly_expenses.tail(6).items()},
                    "monthly_income": {str(k): float(v) for k, v in monthly_income.tail(6).items()} if len(monthly_income) > 0 else {},
                    "avg_monthly_expense": round(float(monthly_expenses.mean()), 2),
                    "avg_monthly_income": round(float(monthly_income.mean()), 2) if len(monthly_income) > 0 else 0
                },
                "method": "enhanced_trend_analysis",
                "prophet_forecast": prophet_forecast,
                "message": "Enhanced forecast generated successfully"
            }
    except Exception as e:
        # Fallback to simple average
        avg_expense = expenses_df["amount"].sum() / max(len(monthly_expenses), 1) * -1
        return {
            "forecast": {
                "next_month_expenses": round(avg_expense, 2),
                "next_month_income": 0,
                "next_month_net": round(-avg_expense, 2)
            },
            "method": "simple_average",
            "message": f"Using simple average due to error: {str(e)}"
        }

def _calculate_trend_forecast(monthly_series):
    """Calculate trend-based forecast using linear regression."""
    if len(monthly_series) < 2:
        return {"forecast": monthly_series.iloc[-1] if len(monthly_series) > 0 else 0, "trend": "stable", "change_pct": 0}
    
    # Create time index
    x = list(range(len(monthly_series)))
    y = monthly_series.values
    
    # Simple linear regression
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(x[i] ** 2 for i in range(n))
    
    # Calculate slope and intercept
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
    intercept = (sum_y - slope * sum_x) / n
    
    # Forecast next period
    next_x = len(monthly_series)
    forecast = slope * next_x + intercept
    
    # Determine trend
    if abs(slope) < monthly_series.mean() * 0.05:  # Less than 5% change
        trend = "stable"
    elif slope > 0:
        trend = "increasing"
    else:
        trend = "decreasing"
    
    # Calculate percentage change
    recent_avg = monthly_series.tail(3).mean()
    change_pct = (slope / recent_avg * 100) if recent_avg != 0 else 0
    
    return {
        "forecast": max(forecast, 0),  # Ensure non-negative
        "trend": trend,
        "change_pct": round(change_pct, 1)
    }

def _forecast_by_category(expenses_df):
    """Forecast expenses by category."""
    if expenses_df.empty:
        return {}
    
    category_forecasts = {}
    expenses_df["month"] = expenses_df["date"].dt.to_period("M")
    
    for category in expenses_df["category"].unique():
        cat_data = expenses_df[expenses_df["category"] == category]
        monthly_cat = cat_data.groupby("month")["amount"].sum().abs()
        
        if len(monthly_cat) >= 2:
            trend = _calculate_trend_forecast(monthly_cat)
            category_forecasts[category] = {
                "forecast": round(trend["forecast"], 2),
                "trend": trend["trend"],
                "avg_monthly": round(monthly_cat.mean(), 2)
            }
    
    return category_forecasts

def _calculate_seasonal_adjustment(monthly_series):
    """Calculate seasonal adjustment factor."""
    if len(monthly_series) < 12:
        return 1.0  # No seasonal adjustment if less than a year of data
    
    # Simple seasonal adjustment based on month-to-month variation
    recent_months = monthly_series.tail(3)
    yearly_avg = monthly_series.tail(12).mean()
    recent_avg = recent_months.mean()
    
    # Adjustment factor (1.0 = no change, >1.0 = increase, <1.0 = decrease)
    adjustment = recent_avg / yearly_avg if yearly_avg != 0 else 1.0
    return max(0.5, min(2.0, adjustment))  # Cap between 0.5x and 2x

def _prophet_forecast_optimized(monthly_series):
    """Optimized Prophet forecast with reduced processing time."""
    try:
        # Prepare data for Prophet
        df_prophet = pd.DataFrame({
            "ds": pd.to_datetime(monthly_series.index.astype(str)),
            "y": monthly_series.values
        })
        
        # Use simpler Prophet configuration for speed
        model = Prophet(
            yearly_seasonality=False,  # Disabled for speed
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive',  # Faster than multiplicative
            uncertainty_samples=100  # Reduced from default 1000
        )
        
        model.fit(df_prophet)
        
        # Forecast only next month
        future = model.make_future_dataframe(periods=1, freq="M")
        forecast = model.predict(future)
        
        next_month = forecast.iloc[-1]
        
        return {
            "forecast": round(max(next_month["yhat"], 0), 2),
            "confidence_lower": round(max(next_month["yhat_lower"], 0), 2),
            "confidence_upper": round(next_month["yhat_upper"], 2)
        }
    except Exception:
        return None

def detect_recurring_expenses(db):
    """Detect recurring expenses like subscriptions and rent."""
    results = db.query(Transaction).filter(Transaction.amount < 0).all()
    df = pd.DataFrame([{
        "date": t.date,
        "description": t.description,
        "amount": t.amount,
        "category": t.category
    } for t in results])

    if df.empty or len(df) < 3:
        return []

    # Group by description and amount to find potential recurring expenses
    recurring_candidates = []

    # Look for transactions with similar descriptions and amounts that occur regularly
    grouped = df.groupby(['description', 'amount']).agg({
        'date': ['count', 'min', 'max'],
        'category': 'first'
    }).reset_index()

    # Flatten column names
    grouped.columns = ['description', 'amount', 'count', 'first_date', 'last_date', 'category']

    # Filter for transactions that appear multiple times
    potential_recurring = grouped[grouped['count'] >= 3]

    for _, row in potential_recurring.iterrows():
        # Calculate average interval between transactions
        desc_transactions = df[
            (df['description'] == row['description']) &
            (df['amount'] == row['amount'])
        ].sort_values('date')

        if len(desc_transactions) >= 3:
            # Calculate intervals between consecutive transactions
            intervals = []
            dates = desc_transactions['date'].tolist()
            for i in range(1, len(dates)):
                interval = (dates[i] - dates[i-1]).days
                intervals.append(interval)

            avg_interval = sum(intervals) / len(intervals)

            # Consider it recurring if average interval is between 25-40 days (monthly)
            if 25 <= avg_interval <= 40:
                recurring_candidates.append({
                    "description": row['description'],
                    "amount": abs(row['amount']),
                    "frequency": "monthly",
                    "avg_interval_days": round(avg_interval, 1),
                    "occurrences": int(row['count']),
                    "category": row['category'] or "Uncategorized",
                    "first_date": row['first_date'].isoformat(),
                    "last_date": row['last_date'].isoformat()
                })

    return recurring_candidates
