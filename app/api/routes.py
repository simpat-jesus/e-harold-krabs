from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.crud import insert_transaction, get_db
from db.models import Transaction
from services.csv_parser import parse_csv
from services.pdf_parser import parse_pdf
from services.insights import get_summary, get_categories, get_monthly_trends
import pandas as pd
from io import StringIO
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"CSV upload request received: {file.filename}, size: {file.size} bytes")
    try:
        content = await file.read()
        transactions = parse_csv(content)
        logger.info(f"CSV parsing complete, extracted {len(transactions)} transactions")

        inserted = []
        for tx in transactions:
            inserted.append(insert_transaction(db, tx))

        logger.info(f"Successfully inserted {len(inserted)} transactions into database")
        return {"inserted": len(inserted)}
    except Exception as e:
        logger.error(f"CSV upload failed: {str(e)}")
        return {"error": f"Failed to process CSV: {str(e)}"}

@router.post("/upload-pdf")
async def upload_pdf(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"PDF upload request received: {file.filename}, size: {file.size} bytes")
    try:
        content = await file.read()
        logger.info(f"PDF file read successfully, {len(content)} bytes")

        transactions = parse_pdf(content)
        logger.info(f"PDF parsing complete, extracted {len(transactions)} transactions")

        inserted = []
        for tx in transactions:
            inserted.append(insert_transaction(db, tx))

        logger.info(f"Successfully inserted {len(inserted)} transactions into database")
        return {"message": "PDF processed", "transactions": len(inserted)}
    except Exception as e:
        logger.error(f"PDF upload failed: {str(e)}")
        return {"error": f"Failed to process PDF: {str(e)}"}

@router.get("/insights/summary")
async def insights_summary(request: Request, db: Session = Depends(get_db)):
    logger.info("Request for insights summary")
    result = get_summary(db)
    logger.info(f"Summary generated: {len(result)} items")
    return result

@router.get("/insights/categories")
async def insights_categories(request: Request, db: Session = Depends(get_db)):
    logger.info("Request for insights categories")
    result = get_categories(db)
    logger.info(f"Categories generated: {len(result)} items")
    return result

@router.get("/insights/monthly")
async def insights_monthly(request: Request, db: Session = Depends(get_db)):
    logger.info("Request for insights monthly trends")
    result = get_monthly_trends(db)
    logger.info(f"Monthly trends generated: {len(result)} items")
    return result

@router.get("/export/csv")
async def export_csv(request: Request, db: Session = Depends(get_db)):
    results = db.query(Transaction).all()
    if not results:
        raise HTTPException(status_code=404, detail="No transactions to export")
    
    df = pd.DataFrame([{
        "date": t.date,
        "description": t.description,
        "amount": t.amount,
        "category": t.category
    } for t in results])
    
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    return {"csv": csv_content}
