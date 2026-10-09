import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.pdf_service import validate_pdf_bytes, PDFProcessingError
from backend.app.services.segmentation_service import segment_nda_text
from backend.app.services.risk_service import evaluate_document_risk, assess_clause_risk
from preprocessing.clause_segmenter_v3 import ClauseV3
import numpy as np


def test_validate_pdf_bytes_empty():
    with pytest.raises(PDFProcessingError, match="empty"):
        validate_pdf_bytes(b"", "test.pdf")


def test_validate_pdf_bytes_invalid_extension():
    with pytest.raises(PDFProcessingError, match="extension"):
        validate_pdf_bytes(b"%PDF-1.4 test", "test.txt")


def test_validate_pdf_bytes_invalid_header():
    with pytest.raises(PDFProcessingError, match="header"):
        validate_pdf_bytes(b"NOT_A_PDF_FILE", "test.pdf")


def test_validate_pdf_bytes_success():
    # Should not raise exception
    validate_pdf_bytes(b"%PDF-1.5 test header content", "test.pdf")


def test_segmentation_adapter():
    sample_text = (
        "CONFIDENTIALITY AGREEMENT\n\n"
        "1. Definition of Confidential Information. The receiving party agrees to hold "
        "all confidential information in strict confidence and shall not disclose it to third parties.\n\n"
        "2. Term and Termination. This Agreement shall terminate five years from the Effective Date."
    )
    segmented = segment_nda_text(sample_text, document_id="doc_test")
    assert segmented.document_id == "doc_test"
    assert segmented.num_clauses >= 2
    assert len(segmented.clauses) == segmented.num_clauses


def test_risk_assessment_clause_levels():
    assert assess_clause_risk(["Liability for Damages"]) == "HIGH"
    assert assess_clause_risk(["Definition of Confidential Information"]) == "MEDIUM"
    assert assess_clause_risk(["Party Identification"]) == "LOW"


def test_risk_assessment_document_evaluation():
    c1 = ClauseV3("d1", "c1", "Liability text", 0, 10, "legal_clause", False)
    c2 = ClauseV3("d1", "c2", "Term text", 11, 20, "legal_clause", False)
    clauses = [c1, c2]

    # Create dummy probability matrix (2 clauses, 14 categories)
    probs = np.zeros((2, 14), dtype=np.float32)
    # Index 7 = Liability for Damages, Index 9 = Term and Termination
    probs[0, 7] = 0.85
    probs[1, 9] = 0.75

    eval_res = evaluate_document_risk(clauses, probs, threshold=0.60)
    assert eval_res["high_risk_clause_count"] == 2
    assert eval_res["overall_risk_index"] >= 60.0
    assert eval_res["risk_status"] == "HIGH RISK"
    assert "DO NOT SIGN" in eval_res["recommendation"]
