import pandas as pd
import io

def parse_csv(content):
    df = pd.read_csv(io.BytesIO(content))
    transactions = []
    for _, row in df.iterrows():
        tx = {
            "date": str(pd.to_datetime(row["date"]).date()),
            "description": row["description"],
            "amount": float(row["amount"]),
            "category": row.get("category", None),
            "payment_method": row.get("payment_method", None),
        }
        transactions.append(tx)
    return transactions
