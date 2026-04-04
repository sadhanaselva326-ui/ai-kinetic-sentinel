import os
from celery import Celery
from services.extraction import extract_text
from services.ai_service import analyze_document_text
from utils.helpers import decode_base64_file

celery_app = Celery(
    "document_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

@celery_app.task(bind=True, name="process_document_task")
def process_document_task(self, file_base64: str, file_type: str):
    """
    Celery task to handle the extraction and AI analysis.
    """
    # Decode base64 string to bytes inside the task
    file_bytes = decode_base64_file(file_base64)
    
    # 1. Extract Text
    text = extract_text(file_bytes, file_type)
    
    if not text:
        raise ValueError("Processed document is empty or contains no readable text.")
    
    # 2. Analyze using AI
    result = analyze_document_text(text)
    
    return result
