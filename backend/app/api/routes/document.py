import uuid
import logging
from typing import Optional, List
from fastapi import APIRouter, File, UploadFile, Query, HTTPException, status
from fastapi.responses import Response

from backend.app.schemas.document import (
    DocumentAnalysisResponse,
    ClauseAnalysis,
    CategoryPrediction,
    DocumentListResponse,
    DocumentSummaryItem,
)
from backend.app.services.pdf_service import extract_pdf_content, PDFProcessingError
from backend.app.services.segmentation_service import segment_nda_text
from backend.app.services.model_service import predict_clause_categories
from backend.app.services.risk_service import evaluate_document_risk
from backend.app.services.report_service import generate_pdf_report
from backend.app.db.database import (
    save_document_analysis,
    list_document_analyses,
    get_document_analysis,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/documents/analyze",
    response_model=DocumentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze NDA PDF Document",
    description="Upload an NDA PDF contract to extract text, segment clauses, classify legal categories, and calculate risk index.",
)
async def analyze_document(
    file: UploadFile = File(..., description="NDA PDF document file"),
    threshold: float = Query(
        default=0.60,
        ge=0.10,
        le=0.90,
        description="Classification probability threshold (default 0.60)",
    ),
    model_choice: str = Query(
        default="legal_roberta",
        pattern="^(legal_roberta|legal_bert|deberta_v3|exp03)$",
        description="Transformer model checkpoint choice",
    ),
) -> DocumentAnalysisResponse:
    """Process uploaded PDF, segment clauses, predict 14 legal categories, and assess document risk."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing from upload request."
        )

    doc_uuid = f"doc_{uuid.uuid4().hex[:10]}"

    try:
        content = await file.read()
        text, pdf_result = extract_pdf_content(content=content, filename=file.filename)
    except PDFProcessingError as pe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(pe)
        )
    except Exception as e:
        logger.error(f"Error processing uploaded PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while reading the PDF document."
        )

    # 1. Segment text into clauses
    segmented_doc = segment_nda_text(text=text, document_id=doc_uuid)
    
    if not segmented_doc.clauses:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid clauses could be segmented from the uploaded document."
        )

    # 2. Extract clause texts for model inference
    clause_texts = [c.text for c in segmented_doc.clauses]

    # 3. Model inference using selected checkpoint
    try:
        probabilities = predict_clause_categories(
            clause_texts=clause_texts,
            model_key=model_choice,
            batch_size=16,
            max_length=256
        )
    except Exception as me:
        logger.error(f"Model inference failure: {me}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification model inference failed: {str(me)}"
        )

    # 4. Risk evaluation
    risk_report = evaluate_document_risk(
        clauses=segmented_doc.clauses,
        probabilities=probabilities,
        threshold=threshold
    )

    # 5. Format response schema
    formatted_clauses = [
        ClauseAnalysis(
            clause_id=c["clause_id"],
            text=c["text"],
            start=c["start"],
            end=c["end"],
            segment_type=c["segment_type"],
            is_suspicious=c["is_suspicious"],
            predicted_categories=[
                CategoryPrediction(category=p["category"], confidence=p["confidence"])
                for p in c["predicted_categories"]
            ],
            risk_level=c["risk_level"],
        )
        for c in risk_report["clauses"]
    ]

    response_obj = DocumentAnalysisResponse(
        document_id=doc_uuid,
        filename=file.filename,
        page_count=pdf_result.page_count,
        character_count=pdf_result.character_count,
        word_count=pdf_result.word_count,
        total_clauses=len(formatted_clauses),
        high_risk_clause_count=risk_report["high_risk_clause_count"],
        medium_risk_clause_count=risk_report["medium_risk_clause_count"],
        overall_risk_index=risk_report["overall_risk_index"],
        risk_status=risk_report["risk_status"],
        recommendation=risk_report["recommendation"],
        advice=risk_report["advice"],
        detected_categories=risk_report["detected_categories"],
        clauses=formatted_clauses,
    )

    # 6. Save successful analysis to SQLite history database
    try:
        save_document_analysis(
            analysis_dict=response_obj.model_dump(),
            model_choice=model_choice,
            threshold=threshold
        )
    except Exception as dbe:
        logger.warning(f"Failed to persist analysis to database: {dbe}")

    return response_obj


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Recent Document Analysis History",
    description="Retrieve paginated list of recent document analysis summaries.",
)
async def list_documents(
    skip: int = Query(default=0, ge=0, description="Pagination skip offset"),
    limit: int = Query(default=20, ge=1, le=100, description="Pagination page limit"),
) -> DocumentListResponse:
    """Retrieve document history list with pagination."""
    items_raw, total_count = list_document_analyses(skip=skip, limit=limit)
    items = [DocumentSummaryItem(**item) for item in items_raw]
    return DocumentListResponse(
        total_count=total_count,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get(
    "/documents/{document_id}",
    response_model=DocumentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Document Analysis by ID",
    description="Retrieve full document analysis result by unique document ID.",
)
async def get_document(document_id: str) -> DocumentAnalysisResponse:
    """Fetch stored document analysis result."""
    data = get_document_analysis(document_id=document_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document analysis with ID '{document_id}' not found."
        )
    return DocumentAnalysisResponse(**data)


@router.get(
    "/documents/{document_id}/report",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Download Executive PDF Risk Assessment Report",
    description="Generate and download executive PDF risk report from stored analysis data.",
)
async def download_document_report(document_id: str):
    """Generate and stream downloadable PDF risk report."""
    data = get_document_analysis(document_id=document_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document analysis with ID '{document_id}' not found."
        )

    try:
        pdf_bytes = generate_pdf_report(analysis_dict=data)
    except Exception as re:
        logger.error(f"Failed to generate PDF report for {document_id}: {re}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF report: {str(re)}"
        )

    safe_filename = f"NDA_Risk_Report_{document_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"'
        }
    )
