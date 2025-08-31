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
    """Forecast next month's expenses using Prophet."""
    results = db.query(Transaction).filter(Transaction.amount < 0).all()
    df = pd.DataFrame([{
        "date": t.date,
        "amount": t.amount
    } for t in results])

    if len(df) < 30:  # Need sufficient data for forecasting
        return {"forecast": None, "message": "Insufficient data for forecasting (need at least 30 transactions)"}

    # Aggregate by month
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    monthly_expenses = df.groupby("month")["amount"].sum().abs().reset_index()
    monthly_expenses["month"] = pd.to_datetime(monthly_expenses["month"])
    monthly_expenses = monthly_expenses.rename(columns={"month": "ds", "amount": "y"})

    # Sort by date
    monthly_expenses = monthly_expenses.sort_values("ds")

    # Fit Prophet model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )

    try:
        model.fit(monthly_expenses)

        # Forecast next month
        future = model.make_future_dataframe(periods=1, freq="M")
        forecast = model.predict(future)

        next_month_forecast = forecast.iloc[-1]["yhat"]
        confidence_lower = forecast.iloc[-1]["yhat_lower"]
        confidence_upper = forecast.iloc[-1]["yhat_upper"]

        return {
            "forecast": round(next_month_forecast, 2),
            "confidence_lower": round(confidence_lower, 2),
            "confidence_upper": round(confidence_upper, 2),
            "message": "Forecast generated successfully"
        }

    except Exception as e:
        return {"forecast": None, "message": f"Forecasting failed: {str(e)}"}

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
