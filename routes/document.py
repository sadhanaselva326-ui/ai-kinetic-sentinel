from fastapi import APIRouter, Depends, HTTPException, status
from models.schemas import DocumentAnalyzeRequest, DocumentAnalyzeResponse, EntitySchema
from utils.security import get_api_key
from utils.helpers import decode_base64_file
from services.extraction import extract_text
from services.ai_service import analyze_document_text

router = APIRouter()

@router.post(
    "/document-analyze",
    response_model=DocumentAnalyzeResponse,
    responses={
        400: {"description": "Bad Request (e.g., Invalid Base64)"},
        401: {"description": "Unauthorized"},
        422: {"description": "Unprocessable Entity (e.g., Validation or OCR failure)"},
        500: {"description": "Internal Server Error"}
    }
)
def analyze_document(request: DocumentAnalyzeRequest, api_key: str = Depends(get_api_key)):
    try:
        # Decode base64 and extract text directly (no Celery/Redis needed for local dev)
        file_bytes = decode_base64_file(request.fileBase64)
        text = extract_text(file_bytes, request.fileType)

        if not text:
            raise ValueError("Document is empty or contains no readable text.")

        # Run AI analysis directly
        analysis_result = analyze_document_text(text)

        return DocumentAnalyzeResponse(
            status="success",
            fileName=request.fileName,
            summary=analysis_result.get("summary", ""),
            entities=EntitySchema(
                names=analysis_result.get("entities", {}).get("names", []),
                dates=analysis_result.get("entities", {}).get("dates", []),
                organizations=analysis_result.get("entities", {}).get("organizations", []),
                amounts=analysis_result.get("entities", {}).get("amounts", [])
            ),
            sentiment=analysis_result.get("sentiment", "Neutral")
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {str(e)}")
