from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentAnalyzeRequest(BaseModel):
    fileName: str
    fileType: str = Field(..., pattern="^(pdf|docx|image)$", description="Must be pdf, docx, or image")
    fileBase64: str

class EntitySchema(BaseModel):
    names: List[str] = []
    dates: List[str] = []
    organizations: List[str] = []
    amounts: List[str] = []

class DocumentAnalyzeResponse(BaseModel):
    status: str
    fileName: str
    summary: str
    entities: EntitySchema
    sentiment: str = Field(..., pattern="^(Positive|Neutral|Negative)$")
    
class ErrorResponse(BaseModel):
    detail: str
