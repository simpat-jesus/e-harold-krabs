import os
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Banks
credit_bank = "Krabby Patty Credit Union"
savings_bank = "Pearl's Savings Bank"

# Account types
account_types = {
    credit_bank: "Credit Card",
    savings_bank: "Savings Account"
}

# Folder
output_folder = "test data"

# Function to generate transactions for a month
def generate_transactions(bank, year, month):
    transactions = []
    # Get number of days in month
    if month == 2:
        days = 28 if year % 4 != 0 else 29
    elif month in [4,6,9,11]:
        days = 30
    else:
        days = 31

    # Recurring monthly
    if bank == credit_bank:
        transactions.append((1, "Krabby Patty Magazine Subscription", -10.00))
        transactions.append((15, "Gym Membership", -50.00))
    else:
        transactions.append((1, "Rent Payment", -1000.00))
        transactions.append((15, "Utility Bill", -200.00))

    # Bi-weekly salary for savings
    if bank == savings_bank:
        for day in range(1, days+1, 15):
            if day <= days:
                transactions.append((day, "Salary Deposit", 2000.00))

    # Emergency transactions
    emergency_count = random.randint(1, 3)
    for _ in range(emergency_count):
        day = random.randint(1, days)
        if bank == credit_bank:
            desc = random.choice(["Doctor Visit", "Car Repair", "Emergency Purchase"])
            amount = -random.randint(100, 500)
        else:
            desc = random.choice(["Medical Expense", "Car Maintenance", "Unexpected Bill"])
            amount = -random.randint(50, 300)
        transactions.append((day, desc, amount))

    # Other transactions
    other_count = random.randint(15, 25)
    for _ in range(other_count):
        day = random.randint(1, days)
        if bank == credit_bank:
            desc = random.choice(["Grocery Store", "Online Purchase", "Restaurant", "Gas Station", "Pharmacy"])
            amount = -random.randint(10, 200)
        else:
            desc = random.choice(["ATM Withdrawal", "Online Transfer", "Bill Payment", "Grocery", "Entertainment"])
            amount = random.choice([-random.randint(20, 500), random.randint(50, 300)])  # mix debit/credit
        transactions.append((day, desc, amount))

    # Sort by day
    transactions.sort(key=lambda x: x[0])

    return transactions

# Function to create PDF
def create_pdf(bank, year, month, transactions):
    filename = f"{output_folder}/{bank.replace(' ', '_')}_{year}_{month:02d}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph(f"{bank} - {account_types[bank]} Statement", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Period
    period = Paragraph(f"Statement Period: {datetime(year, month, 1).strftime('%B %Y')}", styles['Normal'])
    elements.append(period)
    elements.append(Spacer(1, 12))

    # Account Number
    account_num = f"Account Number: ****{random.randint(1000,9999)}"
    elements.append(Paragraph(account_num, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Opening Balance
    opening_balance = round(random.uniform(500, 2000), 2)
    elements.append(Paragraph(f"Opening Balance: ${opening_balance:.2f}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Transactions Table
    data = [['Date', 'Description', 'Amount']]
    balance = opening_balance
    for day, desc, amt in transactions:
        date_str = f"{year}-{month:02d}-{day:02d}"
        data.append([date_str, desc, f"${amt:.2f}"])
        balance += amt

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Closing Balance
    elements.append(Paragraph(f"Closing Balance: ${balance:.2f}", styles['Normal']))

    doc.build(elements)

# Main
if __name__ == "__main__":
    banks = [credit_bank, savings_bank]
    years = [2023, 2024]
    for bank in banks:
        for year in years:
            for month in range(1, 13):
                transactions = generate_transactions(bank, year, month)
                create_pdf(bank, year, month, transactions)
                print(f"Generated {bank} {year}-{month:02d}")
