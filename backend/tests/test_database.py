import pytest
import tempfile
import sqlite3
from pathlib import Path
from backend.app.db.database import (
    init_db,
    save_document_analysis,
    list_document_analyses,
    get_document_analysis,
)


@pytest.fixture
def tmp_db_path():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        p = Path(tmp.name)
    yield p
    if p.exists():
        p.unlink()


def test_init_db(tmp_db_path):
    init_db(tmp_db_path)
    assert tmp_db_path.exists()

    # Test safe idempotent init
    init_db(tmp_db_path)
    assert tmp_db_path.exists()


def test_save_and_get_document_analysis(tmp_db_path):
    sample_analysis = {
        "document_id": "doc_test123",
        "filename": "sample_contract.pdf",
        "page_count": 3,
        "character_count": 4500,
        "word_count": 720,
        "total_clauses": 15,
        "high_risk_clause_count": 1,
        "medium_risk_clause_count": 2,
        "overall_risk_index": 65.0,
        "risk_status": "HIGH RISK",
        "recommendation": "DO NOT SIGN",
        "advice": "Review flagged covenants.",
        "detected_categories": ["Liability for Damages", "Intellectual Property"],
        "clauses": []
    }

    save_document_analysis(sample_analysis, model_choice="legal_roberta", threshold=0.60, db_path=tmp_db_path)

    fetched = get_document_analysis("doc_test123", db_path=tmp_db_path)
    assert fetched is not None
    assert fetched["document_id"] == "doc_test123"
    assert fetched["filename"] == "sample_contract.pdf"
    assert fetched["overall_risk_index"] == 65.0


def test_list_document_analyses(tmp_db_path):
    for i in range(5):
        sample = {
            "document_id": f"doc_{i}",
            "filename": f"contract_{i}.pdf",
            "page_count": 2,
            "total_clauses": 10,
            "high_risk_clause_count": 0,
            "medium_risk_clause_count": 1,
            "overall_risk_index": 15.0,
            "risk_status": "LOW RISK",
            "recommendation": "SAFE TO SIGN",
            "advice": "Low risk.",
            "detected_categories": ["Confidentiality Obligations"],
            "clauses": []
        }
        save_document_analysis(sample, db_path=tmp_db_path)

    items, total_count = list_document_analyses(skip=0, limit=3, db_path=tmp_db_path)
    assert total_count == 5
    assert len(items) == 3


def test_get_unknown_document_id(tmp_db_path):
    fetched = get_document_analysis("non_existent_id", db_path=tmp_db_path)
    assert fetched is None
