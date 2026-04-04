from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import document
from utils.errors import DocumentProcessingError, InvalidBase64Error, OCRFailureError

app = FastAPI(
    title="Document Analysis API",
    description="AI-powered document analysis system using FastAPI and Celery.",
    version="1.0.0"
)

# Allow CORS for local HTML testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(DocumentProcessingError)
async def document_processing_exception_handler(request: Request, exc: DocumentProcessingError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc.message)},
    )

@app.exception_handler(InvalidBase64Error)
async def invalid_base64_exception_handler(request: Request, exc: InvalidBase64Error):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc.message)},
    )
    
@app.exception_handler(OCRFailureError)
async def ocr_failure_exception_handler(request: Request, exc: OCRFailureError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc.message)},
    )

# Include Routers
app.include_router(document.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
