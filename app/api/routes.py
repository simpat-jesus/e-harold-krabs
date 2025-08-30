from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.crud import insert_transaction, get_db
from db.models import Transaction
from services.csv_parser import parse_csv
from services.pdf_parser import parse_pdf
from services.insights import get_summary, get_categories, get_monthly_trends
import pandas as pd
from io import StringIO

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        transactions = parse_csv(content)
        inserted = []
        for tx in transactions:
            inserted.append(insert_transaction(db, tx))
        return {"inserted": len(inserted)}
    except Exception as e:
        return {"error": f"Failed to process CSV: {str(e)}"}

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        transactions = parse_pdf(content)
        inserted = []
        for tx in transactions:
            inserted.append(insert_transaction(db, tx))
        return {"message": "PDF processed", "transactions": len(inserted)}
    except Exception as e:
        return {"error": f"Failed to process PDF: {str(e)}"}

@router.get("/insights/summary")
def insights_summary(db: Session = Depends(get_db)):
    return get_summary(db)

@router.get("/insights/categories")
def insights_categories(db: Session = Depends(get_db)):
    return get_categories(db)

@router.get("/insights/monthly")
def insights_monthly(db: Session = Depends(get_db)):
    return get_monthly_trends(db)

@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    results = db.query(Transaction).all()
    if not results:
        raise HTTPException(status_code=404, detail="No transactions to export")
    
    df = pd.DataFrame([{
        "date": t.date,
        "description": t.description,
        "amount": t.amount,
        "category": t.category,
        "payment_method": t.payment_method
    } for t in results])
    
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    return {"csv": csv_content}
