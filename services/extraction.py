import io
import pypdf
import docx
import pytesseract
from PIL import Image
from utils.errors import DocumentProcessingError, OCRFailureError

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise DocumentProcessingError(f"Failed to process DOCX: {str(e)}")

def extract_text_from_image(file_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        # Optional: Can add image preprocessing here before OCR
        text = pytesseract.image_to_string(image)
        if not text.strip():
            # If tesseract succeeds but finds no text, just return empty, handling it at higher level
            return ""
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
