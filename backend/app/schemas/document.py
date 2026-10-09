from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class CategoryPrediction(BaseModel):
    """Predicted category name and confidence score."""
    category: str = Field(description="Legal category name")
    confidence: float = Field(description="Sigmoid probability score (0.0 - 1.0)")


class ClauseAnalysis(BaseModel):
    """Analyzed legal clause with predictions and risk level."""
    clause_id: str = Field(description="Unique clause identifier")
    text: str = Field(description="Clause text content")
    start: int = Field(description="Character start offset in text")
    end: int = Field(description="Character end offset in text")
    segment_type: str = Field(description="Segment type classification")
    is_suspicious: bool = Field(description="Flag for suspicious formatting/length")
    predicted_categories: List[CategoryPrediction] = Field(description="List of predicted categories")
    risk_level: str = Field(description="Clause risk level (LOW, MEDIUM, HIGH)")


class DocumentAnalysisResponse(BaseModel):
    """Response schema for POST /api/v1/documents/analyze endpoint."""
    document_id: str = Field(description="Document ID")
    filename: str = Field(description="Uploaded PDF filename")
    page_count: int = Field(description="Total PDF page count")
    character_count: int = Field(description="Total extracted character count")
    word_count: int = Field(description="Total extracted word count")
    total_clauses: int = Field(description="Total segmented clauses")
    high_risk_clause_count: int = Field(description="Count of high-risk clauses")
    medium_risk_clause_count: int = Field(description="Count of medium-risk clauses")
    overall_risk_index: float = Field(description="Document Risk Index percentage (0.0 - 100.0%)")
    risk_status: str = Field(description="Risk level label (LOW RISK, MEDIUM RISK, HIGH RISK)")
    recommendation: str = Field(description="Actionable signing decision recommendation")
    advice: str = Field(description="Guidance and advice text")
    detected_categories: List[str] = Field(description="List of detected legal categories across document")
    clauses: List[ClauseAnalysis] = Field(description="List of analyzed clauses")
    disclaimer: str = Field(
        default="Automated AI analysis report for informational purposes. Does not constitute legal advice.",
        description="Disclaimer note"
    )


class DocumentSummaryItem(BaseModel):
    """Summary item for GET /api/v1/documents history endpoint."""
    document_id: str = Field(description="Unique document ID")
    filename: str = Field(description="Original uploaded filename")
    upload_timestamp: str = Field(description="ISO 8601 upload timestamp")
    page_count: int = Field(description="Page count")
    total_clauses: int = Field(description="Total clauses")
    high_risk_clause_count: int = Field(description="High-risk clauses count")
    medium_risk_clause_count: int = Field(description="Medium-risk clauses count")
    model_choice: str = Field(description="Model checkpoint choice used")
    threshold: float = Field(description="Decision threshold used")
    overall_risk_index: float = Field(description="Weighted Risk Index percentage")
    risk_status: str = Field(description="Risk status")
    recommendation: str = Field(description="Recommendation string")
    detected_categories: List[str] = Field(description="Detected categories")


class DocumentListResponse(BaseModel):
    """Paginated list response for GET /api/v1/documents."""
    total_count: int = Field(description="Total documents in history database")
    skip: int = Field(description="Pagination skip offset")
    limit: int = Field(description="Pagination limit size")
    items: List[DocumentSummaryItem] = Field(description="List of document analysis summaries")
