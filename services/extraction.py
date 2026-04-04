import os
import io
import pypdf
import docx
import pytesseract
from PIL import Image

# For local Windows development, set TESSERACT_CMD in your .env
# On Render (Linux), pytesseract finds 'tesseract' in system PATH automatically.
tesseract_cmd = os.getenv("TESSERACT_CMD", "")
if tesseract_cmd and os.path.exists(tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


class DocumentProcessingError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class OCRFailureError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    except Exception as e:
        raise DocumentProcessingError(f"Failed to process PDF: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise DocumentProcessingError(f"Failed to process DOCX: {str(e)}")


def extract_text_from_image(file_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise OCRFailureError(f"OCR failed for image: {str(e)}")


def extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif file_type == "docx":
        return extract_text_from_docx(file_bytes)
    elif file_type == "image":
        return extract_text_from_image(file_bytes)
    else:
        raise DocumentProcessingError(f"Unsupported file type: {file_type}")
