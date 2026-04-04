from services.extraction import extract_text
from services.ai_service import analyze_document_text
from utils.helpers import decode_base64_file


def process_document(file_base64: str, file_type: str) -> dict:
    """
    Directly processes document without Celery/Redis.
    Decodes base64, extracts text, runs AI analysis.
    """
    file_bytes = decode_base64_file(file_base64)
    text = extract_text(file_bytes, file_type)

    if not text:
        raise ValueError("Document is empty or contains no readable text.")

    result = analyze_document_text(text)
    return result
