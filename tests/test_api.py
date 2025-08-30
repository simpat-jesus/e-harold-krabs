import pytest
from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Finance Assistant API" in response.json()["message"]

def test_insights_summary_empty():
    response = client.get("/insights/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_income" in data
    assert "total_expenses" in data
    assert "balance" in data
    assert "transactions" in data
    assert data["total_income"] == 0
    assert data["total_expenses"] == 0
    assert data["balance"] == 0
    assert data["transactions"] == 0

def test_insights_categories_empty():
    response = client.get("/insights/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_insights_monthly_empty():
    response = client.get("/insights/monthly")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

def test_csv_upload_invalid_file():
    # Test with empty file
    response = client.post("/upload-csv", files={"file": ("test.csv", b"", "text/csv")})
    assert response.status_code == 200
    data = response.json()
    assert "inserted" in data

def test_pdf_upload_invalid_file():
    # Test with non-PDF file
    response = client.post("/upload-pdf", files={"file": ("test.txt", b"not a pdf", "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Failed to process PDF" in data["error"]

def test_export_csv_empty():
    response = client.get("/export/csv")
    assert response.status_code == 404  # No transactions to export
    data = response.json()
    assert "detail" in data
