import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.report_service import generate_pdf_report
from backend.app.db.database import save_document_analysis

client = TestClient(app)


def test_generate_pdf_report_bytes():
    sample_analysis = {
        "document_id": "doc_report_test",
        "filename": "nda_agreement.pdf",
        "page_count": 5,
        "character_count": 12000,
        "word_count": 1800,
        "total_clauses": 24,
        "high_risk_clause_count": 2,
        "medium_risk_clause_count": 3,
        "overall_risk_index": 70.0,
        "risk_status": "HIGH RISK",
        "recommendation": "DO NOT SIGN (REQUIRES LEGAL REVISION)",
        "advice": "Review liability clauses.",
        "detected_categories": ["Liability for Damages", "Competition Rights", "Intellectual Property"],
        "clauses": [
            {
                "clause_id": "doc_report_test_clause_001",
                "text": "Liability for damages shall be unlimited under all circumstances.",
                "start": 100,
                "end": 200,
                "segment_type": "legal_clause",
                "is_suspicious": False,
                "predicted_categories": [
                    {"category": "Liability for Damages", "confidence": 0.89}
                ],
                "risk_level": "HIGH"
            }
        ]
    }

    pdf_bytes = generate_pdf_report(sample_analysis)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 500


def test_download_report_endpoint_404():
    response = client.get("/api/v1/documents/non_existent_doc_id/report")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_document_history_and_report():
    # Save a test analysis record
    sample_analysis = {
        "document_id": "doc_hist_test",
        "filename": "history_test.pdf",
        "page_count": 2,
        "character_count": 3000,
        "word_count": 500,
        "total_clauses": 8,
        "high_risk_clause_count": 0,
        "medium_risk_clause_count": 1,
        "overall_risk_index": 15.0,
        "risk_status": "LOW RISK",
        "recommendation": "SAFE TO SIGN",
        "advice": "Low risk.",
        "detected_categories": ["Confidentiality Obligations"],
        "clauses": []
    }
    save_document_analysis(sample_analysis)

    # Test GET /api/v1/documents
    res_list = client.get("/api/v1/documents?skip=0&limit=10")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert "total_count" in list_data
    assert list_data["total_count"] >= 1

    # Test GET /api/v1/documents/{id}
    res_get = client.get("/api/v1/documents/doc_hist_test")
    assert res_get.status_code == 200
    assert res_get.json()["document_id"] == "doc_hist_test"

    # Test GET /api/v1/documents/{id}/report
    res_rep = client.get("/api/v1/documents/doc_hist_test/report")
    assert res_rep.status_code == 200
    assert res_rep.headers["content-type"] == "application/pdf"
    assert res_rep.content.startswith(b"%PDF-")
