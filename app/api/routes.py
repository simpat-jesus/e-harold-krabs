from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.crud import insert_transaction, insert_transactions_batch, get_db
from db.models import Transaction
from services.csv_parser import parse_csv
from services.pdf_parser import parse_pdf
from services.ai_parser import parse_with_ai
from services.insights import get_summary, get_categories, get_monthly_trends, detect_recurring_expenses, detect_anomalies, forecast_expenses
import pandas as pd
from io import StringIO, BytesIO
from fastapi.responses import StreamingResponse
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

        inserted_count = insert_transactions_batch(db, transactions)
        logger.info(f"Successfully inserted {inserted_count} transactions into database (duplicates skipped)")
        return {"inserted": inserted_count}
    except Exception as e:
        logger.error(f"CSV upload failed: {str(e)}")
        return {"error": f"Failed to process CSV: {str(e)}"}

@router.post("/upload-pdf")
async def upload_pdf(request: Request, file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"PDF upload request received: {file.filename}, size: {file.size} bytes")
    try:
        content = await file.read()
        logger.info(f"PDF file read successfully, {len(content)} bytes")

        # Step 1: Extract text from PDF
        extracted_text = parse_pdf(content)
        if not extracted_text:
            return {"error": "Failed to extract text from PDF"}

        # Step 2: Parse transactions with AI
        transactions = parse_with_ai(extracted_text)
        logger.info(f"AI parsing complete, extracted {len(transactions)} transactions")

        inserted_count = insert_transactions_batch(db, transactions)
        logger.info(f"Successfully inserted {inserted_count} transactions into database (duplicates skipped)")
        return {"message": "PDF processed", "transactions": inserted_count}
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

@router.get("/transactions")
async def get_transactions(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all transactions."""
    logger.info("Request for transactions")

    results = db.query(Transaction).all()

    transactions = [{
        "id": t.id,
        "date": t.date.isoformat(),
        "description": t.description,
        "amount": t.amount,
        "category": t.category
    } for t in results]

    logger.info(f"Returned {len(transactions)} transactions")
    return {"transactions": transactions, "total": len(transactions)}

@router.get("/export/excel")
async def export_excel(
    request: Request,
    db: Session = Depends(get_db)
):
    results = db.query(Transaction).all()

    if not results:
        raise HTTPException(status_code=404, detail="No transactions to export")

    df = pd.DataFrame([{
        "date": t.date,
        "description": t.description,
        "amount": t.amount,
        "category": t.category
    } for t in results])

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Transactions", index=False)

    excel_buffer.seek(0)
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=transactions.xlsx"}
    )

@router.get("/export/csv")
async def export_csv(
    request: Request,
    db: Session = Depends(get_db)
):
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

@router.get("/insights/recurring")
async def insights_recurring(request: Request, db: Session = Depends(get_db)):
    logger.info("Request for recurring expenses detection")
    result = detect_recurring_expenses(db)
    logger.info(f"Recurring expenses detected: {len(result)} items")
    return result

@router.get("/insights/anomalies")
async def insights_anomalies(request: Request, db: Session = Depends(get_db)):
    logger.info("Request for anomaly detection")
    result = detect_anomalies(db)
    logger.info(f"Anomalies detected: {len(result)} items")
    return result

@router.get("/insights/forecast")
async def insights_forecast(request: Request, db: Session = Depends(get_db)):
    logger.info("Request for expense forecasting")
    result = forecast_expenses(db)
    logger.info(f"Forecast result: {result.get('message', 'Completed')}")
    return result
