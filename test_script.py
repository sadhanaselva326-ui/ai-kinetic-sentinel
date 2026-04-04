from dotenv import load_dotenv
load_dotenv()
import os
print("API KEY Loaded:", bool(os.getenv("GEMINI_API_KEY")))



# Configure Celery eagerly before importing app
os.environ["CELERY_ALWAYS_EAGER"] = "True"
os.environ["API_SECRET_KEY"] = "super_secure_key_123"

import base64
from fastapi.testclient import TestClient
from main import app
from services import ai_service, processing, extraction

client = TestClient(app)

# Mock extraction
def mock_extract_text(file_bytes, file_type):
    return "This is a dummy extracted text from the document."

processing.extract_text = mock_extract_text



def test_api():
    # Configure eager mode directly on the app just in case
    processing.celery_app.conf.update(task_always_eager=True)
    
    print("Testing health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    print("Health check passed.")

    # Create a dummy PDF file minimal
    dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Count 1\n/Kids [3 0 R]\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000288 00000 n \n0000000376 00000 n \ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n471\n%%EOF\n"
    dummy_base64 = base64.b64encode(dummy_pdf_content).decode('utf-8')

    payload = {
        "fileName": "test.pdf",
        "fileType": "pdf",
        "fileBase64": dummy_base64
    }

    headers = {
        "x-api-key": "super_secure_key_123"
    }

    print("Sending request to /api/document-analyze...")
    response = client.post("/api/document-analyze", json=payload, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    data = response.json()
    print("Response received successfully!")
    print(data)
    
    assert data["status"] == "success"
    assert "summary" in data
    assert "entities" in data
    assert "sentiment" in data

if __name__ == "__main__":
    test_api()
