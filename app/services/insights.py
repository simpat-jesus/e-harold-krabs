import pandas as pd
from db.models import Transaction

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
