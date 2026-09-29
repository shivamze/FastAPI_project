import pytesseract
from PIL import Image
import io
import re
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def perform_ocr(image_bytes: bytes) -> str:
    """Converts image bytes to a PIL Image and extracts raw text."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(image)
    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")

def receipt_to_expense(image_bytes: bytes) -> dict:
    """Hunts for financial data inside the raw OCR text."""
    raw_text = perform_ocr(image_bytes)

    amount_pattern = r'\d+\.\d{2}'
    found_amounts = [float(a) for a in re.findall(amount_pattern, raw_text)]

    estimated_total = max(found_amounts) if found_amounts else 0.0

    date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
    found_dates = re.findall(date_pattern, raw_text)

    estimated_date = found_dates[0] if found_dates else datetime.today().strftime('%Y-%m-%d')

    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
    estimated_title = lines[0] if lines else "Extracted Receipt"

    return {
        "title": estimated_title,
        "amount": estimated_total,
        "transaction_date": estimated_date,
        "category": "Other", # Defaulted as requested
        "raw_text": raw_text
    }