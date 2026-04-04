# AI Document Analysis Backend

A production-ready FastApi application to process, summarize, and analyze documents (PDF, DOCX, Image) via AI, utilizing Celery + Redis for asynchronous processing workloads.

## Features
- **Base64 Document Parsing**: Accepts base64 encoded document files over a REST API.
- **Robust Text Extraction**: 
  - `PyMuPDF` for fast PDF extraction
  - `python-docx` for word documents
  - `pytesseract` for image text OCR
- **AI Analytics**: Uses OpenAI to perform summarization, entity extraction (names, dates, organizations, amounts), and sentiment analysis.
- **Celery Task Queue**: The heavy extraction and AI requests are pushed and managed by a Celery worker to avoid blocking the main server threads unnecessarily.
- **API Security**: Secured via global API key header (`x-api-key`).

## Setup Requirements
1. **Python 3.9+**
2. **Redis**: Must be installed and running on default port `6379`.
3. **Tesseract-OCR**: Required for image extraction.
   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`
   - Windows: Install via unofficial installer and add it to PATH.
4. **OpenAI API Key**: Set your API key in the `.env` file.

## Installation

1. Clone or navigate to the project directory.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   **Important Keys:**
   - `OPENAI_API_KEY`: Required for all AI functionality.
   - `API_SECRET_KEY`: Set a secure string, this is required in your POST requests.

## Running the Application

You need two terminal windows to run both the FastAPI server and the Celery worker.

**1. Start Redis Server** (if not running as a daemon)
```bash
redis-server
```

**2. Start Celery Worker**
```bash
# Windows
celery -A services.processing.celery_app worker --loglevel=info -P gevent

# Mac/Linux
celery -A services.processing.celery_app worker --loglevel=info
```
*(Note for Windows: you might need to install `gevent` via `pip install gevent` since Celery's default prefork pool doesn't work well on Windows).*

**3. Start FastAPI Server**
```bash
uvicorn main:app --reload --port 8000
```

## API Usage

### Endpoint: `POST /api/document-analyze`

**Headers:**
- `x-api-key`: `your_secret_api_key_here` (from `.env`)

**Body (JSON):**
```json
{
  "fileName": "example.pdf",
  "fileType": "pdf",
  "fileBase64": "JVBERi0xLjQu..[truncated base64]..."
}
```

*Note: `fileType` must be one of: `pdf`, `docx`, `image`.*

**Response (JSON):**
```json
{
  "status": "success",
  "fileName": "example.pdf",
  "summary": "This document outlines...",
  "entities": {
    "names": ["John Doe"],
    "dates": ["12-Oct-2023"],
    "organizations": ["OpenAI"],
    "amounts": ["$5000"]
  },
  "sentiment": "Positive"
}
```
