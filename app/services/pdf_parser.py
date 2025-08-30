import pdfplumber
import io

def parse_pdf(content):
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    # TODO: call AI parser (Ollama/OpenAI) to turn text -> structured JSON
    # For now, mock with one example transaction
    return [{
        "date": "2025-08-01",
        "description": "Mock Transaction from PDF",
        "amount": -123.45,
        "category": "Uncategorized",
        "payment_method": "Credit Card"
    }]
