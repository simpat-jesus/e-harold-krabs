import pdfplumber
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_pdf(content) -> str:
    """
    Extract text from PDF content

    Args:
        content: PDF file content as bytes

    Returns:
        Extracted text as string
    """
    logger.info("Starting PDF text extraction process")

    try:
        # Extract text from PDF
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        if not text.strip():
            logger.warning("No text content found in PDF")
            return ""

        logger.info(f"Extracted {len(text)} characters from PDF")
        return text

    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return ""
