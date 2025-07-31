from pydantic import BaseModel, HttpUrl, Field
from typing import List

class ProcessRequest(BaseModel):
    """Request model for document processing"""
    documents: HttpUrl = Field(..., description="URL to the PDF or DOCX document")
    questions: List[str] = Field(..., description="List of questions to answer")

class ProcessResponse(BaseModel):
    """Response model for document processing"""
    answers: List[str] = Field(..., description="List of answers corresponding to the questions")

class LegalAnswer(BaseModel):
    """Model for legal AI response"""
    answer: str
    condition: str
    rationale: str
