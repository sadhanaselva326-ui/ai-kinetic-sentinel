from fastapi import APIRouter, Depends, HTTPException, status
from models.schemas import DocumentAnalyzeRequest, DocumentAnalyzeResponse, EntitySchema
from utils.security import get_api_key
from services.processing import process_document

router = APIRouter()

@router.post(
    "/document-analyze",
    response_model=DocumentAnalyzeResponse,
    responses={
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal Server Error"}
    }
)
def analyze_document(request: DocumentAnalyzeRequest, api_key: str = Depends(get_api_key)):
    try:
        analysis_result = process_document(request.fileBase64, request.fileType)

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {str(e)}")
