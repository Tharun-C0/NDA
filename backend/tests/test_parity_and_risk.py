import pytest
from pathlib import Path
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.model_service import APPROVED_CATEGORIES, predict_clause_categories
from backend.app.services.risk_service import evaluate_document_risk, assess_clause_risk
from backend.app.services.segmentation_service import segment_nda_text
from preprocessing.clause_segmenter_v3 import ClauseV3
from scripts.verify_nda_risk import analyze_document_legacy, analyze_document_parity

ROOT = Path(__file__).resolve().parents[2]
client = TestClient(app)


def test_taxonomy_category_mapping_indices():
    """Verify all 14 taxonomy categories match expected index ordering."""
    assert len(APPROVED_CATEGORIES) == 14
    assert APPROVED_CATEGORIES[0] == "Party Identification"
    assert APPROVED_CATEGORIES[7] == "Liability for Damages"
    assert APPROVED_CATEGORIES[10] == "Intellectual Property"
    assert APPROVED_CATEGORIES[13] == "Additional Information"


def test_unique_clause_risk_counting():
    """Verify clause risk levels are mutually exclusive and sum to total clauses."""
    c1 = ClauseV3("doc1", "c1", "Liability clause", 0, 10, "legal_clause", False)
    c2 = ClauseV3("doc1", "c2", "Definition clause", 11, 20, "legal_clause", False)
    c3 = ClauseV3("doc1", "c3", "Boilerplate clause", 21, 30, "legal_clause", False)
    clauses = [c1, c2, c3]

    probs = np.zeros((3, 14), dtype=np.float32)
    probs[0, 7] = 0.85  # Index 7: Liability for Damages (HIGH)
    probs[1, 3] = 0.75  # Index 3: Definition of Info (MEDIUM)
    probs[2, 0] = 0.90  # Index 0: Party Identification (LOW)

    risk_report = evaluate_document_risk(clauses, probs, threshold=0.60)

    n_high = risk_report["high_risk_clause_count"]
    n_med = risk_report["medium_risk_clause_count"]
    n_total = len(risk_report["clauses"])
    n_low = max(0, n_total - (n_high + n_med))

    assert n_high == 1
    assert n_med == 1
    assert n_low == 1
    assert n_high + n_med + n_low == n_total == 3


def test_api_authoritative_response():
    """Verify API POST /api/v1/documents/analyze returns complete authoritative risk response."""
    test_pdf = ROOT / "25f2299_1.pdf"
    if not test_pdf.exists():
        pytest.skip("Test sample PDF 25f2299_1.pdf not found in project root.")

    with open(test_pdf, "rb") as f:
        response = client.post(
            "/api/v1/documents/analyze?model_choice=legal_roberta&threshold=0.60",
            files={"file": ("25f2299_1.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()

    assert "document_id" in data
    assert "overall_risk_index" in data
    assert "risk_status" in data
    assert "high_risk_clause_count" in data
    assert "medium_risk_clause_count" in data
    assert "clauses" in data

    # Verify mutually exclusive counts
    n_total = data["total_clauses"]
    n_high = data["high_risk_clause_count"]
    n_med = data["medium_risk_clause_count"]
    n_low = n_total - (n_high + n_med)

    assert n_total == len(data["clauses"])
    assert n_low >= 0


def test_terminal_parity_mode_matches_backend(capsys):
    """Verify terminal script --parity mode produces identical output as backend services."""
    test_pdf = ROOT / "25f2299_1.pdf"
    if not test_pdf.exists():
        pytest.skip("Test sample PDF 25f2299_1.pdf not found in project root.")

    # 1. Run backend services directly
    with open(test_pdf, "rb") as f:
        pdf_bytes = f.read()

    from backend.app.services.pdf_service import extract_pdf_content
    text, _ = extract_pdf_content(pdf_bytes, "25f2299_1.pdf")
    segmented_doc = segment_nda_text(text, document_id="25f2299_1")
    clause_texts = [c.text for c in segmented_doc.clauses]
    probs = predict_clause_categories(clause_texts, model_key="legal_roberta")
    backend_report = evaluate_document_risk(segmented_doc.clauses, probs, threshold=0.60)

    # 2. Run terminal parity function
    analyze_document_parity(test_pdf, model_choice="legal_roberta", threshold=0.60)
    captured = capsys.readouterr()

    # Check that output contains backend score & counts
    assert f"{backend_report['overall_risk_index']:.1f}%" in captured.out
    assert f"High-Risk Clauses Found  : {backend_report['high_risk_clause_count']}" in captured.out
    assert f"Medium-Risk Clauses Found: {backend_report['medium_risk_clause_count']}" in captured.out


def test_legacy_exp03_mode_availability(capsys):
    """Verify legacy EXP-03 terminal mode remains available and executes."""
    test_pdf = ROOT / "25f2299_1.pdf"
    ckpt_path = ROOT / "data" / "classification" / "module18_results" / "checkpoints" / "EXP-03"

    if not test_pdf.exists() or not ckpt_path.exists():
        pytest.skip("Required test PDF or EXP-03 checkpoint missing.")

    analyze_document_legacy(test_pdf, ckpt_path, threshold=0.60)
    captured = capsys.readouterr()

    assert "LEGACY EXP-03 MODE" in captured.out
    assert "Document Risk Index" in captured.out
